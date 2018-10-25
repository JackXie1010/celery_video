# coding:utf8
from tornado.gen import coroutine, Return
from base import BaseModel


class UserModel(BaseModel):
    @coroutine
    def get_user_by_id(self, user_id):
        sql = 'select * from user where id=%s' % user_id
        user = yield self.db.get(sql)
        raise Return(user)
