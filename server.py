# coding:utf8
from __future__ import print_function
import tornado.ioloop
import tornado.web
import tornado.httpserver
from handler import index
from tornado.options import options, define
import os

define("port", default=8881, help="run on the given port", type=int)
define('application_name', default='pinpin', type=str)
define('debug', default=False, type=bool)
define('mc_prefix', default='yeah', help='set the mc name', type=str)
define('dev', default=True, type=bool)
tornado.options.parse_command_line()


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            gzip=True,
            debug=False,
            cookie_secret="123",
            static_path=os.path.join(os.path.dirname(__file__), 'front/static'),
        )
        print (os.path.join(os.path.dirname(__file__), 'front/static'))

        handlers = [(r"/", index.IndexHandler),
                    (r"/getVideoInfo", index.GetVideoInfoHandler),
                    ]

        if options.dev:
            print('dev mode')
        super(Application, self).__init__(handlers=handlers, **settings)


def main():
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(options.port)
    io_loop = tornado.ioloop.IOLoop.instance()
    io_loop.start()


if __name__ == '__main__':
    main()

