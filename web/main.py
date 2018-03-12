#!/usr/bin/env python
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from web.handlers import *


def main():
    define('port', default=8888, help='run on the given port', type=int)
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        # view detail
        (r'/api/align/([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})', AlignHandler),
        (r'/api/tree/([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})', TreeHandler),

        # create task
        (r'/api/tree/', CreateTreeHandler),    # return task id
        (r'/api/align/', CreateAlignHandler),  # return task id
        (r'/upload/', UploadFastAHandler),     # return upload file path

        # index
        (r'/', IndexHandler),
        (r'/(index\.html)', tornado.web.StaticFileHandler,
         {'path': os.path.join(os.path.dirname(__file__), 'static/')}),
        (r'/upload/(.*)', tornado.web.StaticFileHandler,
         {'path': os.path.join(os.path.dirname(__file__), '../upload/')})

    ], debug=True, static_path=os.path.join(os.path.dirname(__file__), 'static'))
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
