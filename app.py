# coding=utf-8
import os

from paste.deploy import loadapp

import logging
logging.basicConfig(level=logging.DEBUG)

project_root_dir = '/Users/zhujiongyao/zjy_tests/zjy_webob'  # 项目的根目录
config_dir = os.path.join(project_root_dir, 'configs')  # 配置文件目录

def app():
    paste_config_path = os.path.join(config_dir, 'paste.ini')
    application = loadapp('config:%s' % paste_config_path)
    return application


if __name__ == '__main__':
    import wsgiref.simple_server as wss

    port = 18877
    server = wss.make_server('', port, app())

    print("*" * 80)
    print("STARTING test server")
    print("DANGER! For testing only, do not use in production")
    print("*" * 80)

    server.serve_forever()