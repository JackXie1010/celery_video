#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging

from collections import deque
from tornado.gen import coroutine, Return
from asynctorndb import Connection
from tornado.locks import Lock


class PoolExhaustedError(Exception):
    pass


class PoolClosedError(Exception):
    pass


class Pool(object):

    def __init__(self, host, user, password, database, port=3306, connect_timeout=5,
                 init_command="SET names utf8", max_active=10, idle_timeout=600):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connect_timeout = connect_timeout
        self.init_command = init_command
        self.max_active = max_active  # When zero, there is no limit on the number of connections in the pool
        self.idle_timeout = idle_timeout
        self.active = 0
        self.idle_queue = deque()
        self.closed = False
        self.killer_lock = Lock()
        self.killer = None
        self.killer_idle_at = None

    def active_count(self):
        return self.active

    @coroutine
    def get_killer_connection(self):
        with (yield self.killer_lock.acquire()):
            if self.killer is not None:
                self.killer_idle_at = time.time()
                raise Return(self.killer)
            try:
                self.killer = yield self._create_connection()
                self.killer_idle_at = time.time()
            except Exception as e:
                self.killer = None
                self.killer_idle_at = None
                logging.error(u'create killer connection exception: %s', e)
        raise Return(self.killer)

    @coroutine
    def get_connection(self):

        if self.killer is not None:
            if self.killer_idle_at + 1800 < time.time():
                with (yield self.killer_lock.acquire()):  # avoid kill() and close() at the same time
                    logging.info(u"idle timeout, recycle killer connection: %s", self.killer)
                    self._safe_close(self.killer)
                    self.killer = None
                    self.killer_idle_at = None

        if self.idle_timeout > 0:
            while len(self.idle_queue) > 0:
                c = self.idle_queue[0]
                if c.idle_at + self.idle_timeout > time.time():
                    break

                logging.info(u"idle timeout, recycle stale connection: %s", c)
                c = self.idle_queue.popleft()
                yield self._safe_close(c)  # close the longtime idle connection

        if self.closed:
            raise PoolClosedError(u"connection pool closed.")

        if len(self.idle_queue) > 0:
            self.active += 1
            c = self.idle_queue.pop()
            c.idle_at = time.time()
            raise Return(c)

        if self.max_active == 0 or self.active < self.max_active:
            self.active += 1
            logging.info(u"create new db connection[%s:%s %s]. now active: %d" % (self.host, self.port, self.database, self.active))
            try:
                c = yield self._create_connection()
            except Exception:  # e.g. --> OperationalError: (1040, u'Too many connections')
                self.active -= 1
                raise
            raise Return(c)
        else:
            raise PoolExhaustedError(u"connection pool exhausted. active: %d" % self.active)

    @coroutine
    def _create_connection(self):
        c = Connection(self.host, self.user, self.password, self.database, self.port,
                       connect_timeout=self.connect_timeout, init_command=self.init_command,  charset='utf8')
        yield c.connect()
        yield c.autocommit(True)
        if self.init_command:
            yield c.execute(self.init_command)
        setattr(c, 'idle_at', time.time())
        raise Return(c)

    @coroutine
    def _safe_close(self, conn):
        try:
            yield conn.close()
        except Exception as e:
            logging.warn(u'_safe_close() exception: %s', e)

    @coroutine
    def release_connection(self, conn, discard):
        if conn is None:  # do not get a connection successfully
            return

        self.active -= 1
        if self.closed:  # when pool.close() is called, this connection is being used.
            yield self._safe_close(conn)
            return

        if discard:
            yield self._safe_close(conn)
        else:
            conn.idle_at = time.time()
            self.idle_queue.append(conn)

    @coroutine
    def close(self):
        logging.info(u"pool closing.")
        self.closed = True
        while len(self.idle_queue) > 0:
            c = self.idle_queue.popleft()
            yield self._safe_close(c)
