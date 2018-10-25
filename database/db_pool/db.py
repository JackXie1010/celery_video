#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging

from pool import Pool, PoolExhaustedError, PoolClosedError
from tornado.iostream import StreamClosedError
from tornado.gen import coroutine, Return, with_timeout, TimeoutError


class DB(object):

    def __init__(self, host, user, password, database, port=3306, connect_timeout=5, init_command=None,
                 pool_max_active=0, conn_idle_timeout=600, db_timeout=3):
        self.pool = Pool(host, user, password, database, port, connect_timeout, init_command,
                         pool_max_active, conn_idle_timeout)
        self.db_timeout = db_timeout

    @coroutine
    def _patch_timeout(self, method, query, *args, **kwargs):
        timeout = kwargs.pop('timeout', self.db_timeout)
        assert isinstance(timeout, (float, int, long))
        conn, discard, if_timeout = None, False, False

        try:
            conn = yield self.pool.get_connection()

            if method == 'get':
                future = conn.get(query, *args, **kwargs)
            elif method == 'query':
                future = conn.query(query, *args, **kwargs)
            elif method == 'execute':
                future = conn.execute(query, *args, **kwargs)
            elif method == 'execute_lastrowid':
                future = conn.execute_lastrowid(query, *args, **kwargs)
            elif method == 'execute_rowcount':
                future = conn.execute_rowcount(query, *args, **kwargs)
            elif method == 'executemany':
                future = conn.executemany(query, *args)
            elif method == 'executemany_lastrowid':
                future = conn.executemany_lastrowid(query, *args)
            elif method == 'executemany_rowcount':
                future = conn.executemany_rowcount(query, *args)
            else:
                raise Exception('unknown method in connection, you should never see me.')

            if timeout:
                result = yield with_timeout(time.time() + timeout, future, quiet_exceptions=(StreamClosedError, AttributeError))
                #  File "dbpool/asynctorndb/connection.py", line 274, in recv_packet
                #    recv_data = yield self.connection.stream.read_bytes(bytes_to_read)
                # ignore AttributeError to avoid --> AttributeError: 'NoneType' object has no attribute 'read_bytes'
            else:
                result = yield future
            raise Return(result)

        except Return:
            raise

        except TimeoutError:
            logging.error(u"dbpool sql timeout: connection[%s:%s db:%s] %ss timeout when %s('%s', %s, %s)",
                          conn.host, conn.port, conn.db, timeout, method, query, args, kwargs)
            if_timeout = True
            discard = True  # discard connection to avoid -->  assert self._read_future is None, "Already reading"
            # this connection will be closed immediately, so the client will not wait for the result
            # but the operation in the server side still continuing, unless the server also has timeout limit
            raise

        except StreamClosedError:
            discard = True  # connection closed by the server side (or other reasons), then discard it.
            # e.g. --> the server side use `kill connection_id` to kill this connection
            raise

        except (PoolExhaustedError, PoolClosedError):
            raise

        except Exception as e:
            logging.warn(u"unexpected exception in dbpool._patch_timeout: %s('%s', %s, %s), %s", method, query, args, kwargs, e)
            discard = True  # close it to avoid put a abnormal connection back to the pool, which may cause something bad.
            raise

        finally:
            yield self.pool.release_connection(conn, discard)  # release first

            if if_timeout and method in ('get', 'query'):
                killer = yield self.pool.get_killer_connection()
                if killer is not None:
                    with (yield self.pool.killer_lock.acquire()):
                        try:
                            logging.warn(u'kill thread_id %s', conn.thread_id())
                            yield killer.kill(conn.thread_id())
                        except Exception as e:
                            # InternalError: (1094, u'Unknown thread id: xxxx'), server side's query sql already finish, ignore
                            if len(e.args) > 0 and e.args[0] != 1094:
                                logging.warn(u'unexpected exception in killer.kill(%s), %s', conn.thread_id(), e)
                                yield killer.ping(reconnect=True)

    @coroutine
    def query(self, query, *args, **kwargs):
        result = yield self._patch_timeout('query', query, *args, **kwargs)
        raise Return(result)

    @coroutine
    def get(self, query, *args, **kwargs):
        result = yield self._patch_timeout('get', query, *args, **kwargs)
        raise Return(result)

    @coroutine
    def execute(self, query, *args, **kwargs):
        result = yield self._patch_timeout('execute', query, *args, **kwargs)
        raise Return(result)

    @coroutine
    def execute_lastrowid(self, query, *args, **kwargs):
        result = yield self._patch_timeout('execute_lastrowid', query, *args, **kwargs)
        raise Return(result)

    @coroutine
    def execute_rowcount(self, query, *args, **kwargs):
        result = yield self._patch_timeout('execute_rowcount', query, *args, **kwargs)
        raise Return(result)

    @coroutine
    def executemany(self, query, args, timeout=None):
        timeout = timeout or (3 * self.db_timeout)
        result = yield self._patch_timeout('executemany', query, args, timeout=timeout)
        raise Return(result)

    @coroutine
    def executemany_lastrowid(self, query, args, timeout=None):
        timeout = timeout or (3 * self.db_timeout)
        result = yield self._patch_timeout('executemany_lastrowid', query, args, timeout=timeout)
        raise Return(result)

    @coroutine
    def executemany_rowcount(self, query, args, timeout=None):
        timeout = timeout or (3 * self.db_timeout)
        result = yield self._patch_timeout('executemany_rowcount', query, args, timeout=timeout)
        raise Return(result)

    @coroutine
    def close(self):
        yield self.pool.close()


if __name__ == '__main__':

    import tornado.ioloop
    logging.basicConfig()

    @coroutine
    def test():
        # db = DB(host='10.104.26.243', port=3306, database='articles_at_01',
        #        user='shard_user', password='QB_20!50&@7', init_command="SET names utf8")
        # result = yield db.get('select * from articles where id = %s', 116480579)
        db = DB(host='127.0.0.1', port=3306, database='yld',
                user='root', password='', init_command="SET names utf8")
        result = yield db.get('select sleep(%s)', 3, timeout=1)
        print result
        raise Return(result)

    tornado.ioloop.IOLoop.current().run_sync(test)

