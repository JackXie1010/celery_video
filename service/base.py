# coding:utf8
from model.user import UserModel
from model.index import IndexModel


class BaseService(object):
    def __init__(self, *args, **kwargs):
        super(BaseService, self).__init__(*args, **kwargs)
        self.user_model = UserModel()
        self.index_model = IndexModel()

