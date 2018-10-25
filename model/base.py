# coding:utf8

from database.mysql_pool import async_db as db


class BaseModel(object):
    def __init__(self):
        self.db = db
