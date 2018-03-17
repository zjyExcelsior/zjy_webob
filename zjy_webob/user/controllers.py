# coding=utf-8
from zjy_webob.wsgi import Application


class UserController(Application):
    def get(self, req):
        return {'users': ['<user 1>', '<user 2>', '<user 3>']}

    def get_user(self, req, userid):
        return {'user': '<user 1>'}