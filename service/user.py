# coding:utf8
from .base import BaseService
from tornado.gen import coroutine, Return


class UserService(BaseService):
    @coroutine
    def get_user_by_id(self, user_id):
        data = yield self.user_model.get_user_by_id(user_id)
        raise Return(data)
