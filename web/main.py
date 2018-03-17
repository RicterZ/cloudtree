#!/usr/bin/env python
import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from web.handlers import api, index


def main():
    define('port', default=8889, help='run on the given port', type=int)
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        # api
        (r'/api/view/([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})', api.ResultViewHandler),
        (r'/api/tree/?', api.CreateTreeHandler),      # return task id
        (r'/api/align/?', api.CreateAlignHandler),    # return task id
        (r'/api/pipeline/?', api.PipelineHandler),    # return task id

        # index
        (r'/', index.IndexHandler),
        (r'/upload/?', index.UploadFastAHandler),     # return upload file path
        (r'/create/?', index.CreateTaskHandler),      # return task id
        (r'/login/?', index.LoginHandler),
        (r'/logout/?', index.LogoutHandler),
        (r'/cluster/?', index.ClusterHandler),

        # static
        (r'/upload/(.*)', tornado.web.StaticFileHandler,
         {'path': os.path.join(os.path.dirname(__file__), 'upload/')})

    ], debug=True,
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        cookie_secret='CwvklnbwKLHIOo123rbuihhu0-jioanlsvnbo8FOPAwegbp;o3i1',
        login_url='/login/'
    )

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
