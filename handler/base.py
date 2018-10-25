# coding:utf8
from tornado.web import RequestHandler
from tornado.gen import coroutine
import json
from datetime import datetime, date
from service.user import UserService
from service.index import IndexService


class BaseHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Max-Age", "1728000")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT')
        self.user_serv = UserService()
        self.index_serv = IndexService()
        self._app_err_code = None

    @coroutine
    def options(self, *args, **kwargs):
        self.json_ok('')

    def get_app_err_code(self):
        return self._app_err_code

    def json_ok(self, data='', msg=''):
        callback = self.get_argument('callback', False)
        if not callback:
            self.write({
                'code': 1,
                'msg': msg,
                'data': self.__json(data)
            })
        else:
            self.set_header('content-type', 'text/javascript')
            data = {
                'code': 1,
                'msg': msg,
                'data': self.__json(data)
            }
            self.write("""

                  try{
                      %s(%s)
                  }catch(err){

                  }

                  """ % (callback, self.__dumps(data)))

    def json_err(self, msg=''):
        self.write({
            'code': 0,
            'msg': msg
        })

    def __json(self, data):
        return json.loads(self.__dumps(data))

    def __dumps(self, data):
        return json.dumps(data, cls=JsonEncoder)


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, o)
