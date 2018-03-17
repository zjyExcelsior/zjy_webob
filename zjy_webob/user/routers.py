# coding=utf-8
from zjy_webob.routers import ComposableRouter
from zjy_webob.user.controllers import UserController


class Router(ComposableRouter):

    def add_routes(self, mapper):
        ctrl = UserController()
        mapper.connect('/users', controller=ctrl,
                       conditions=dict(method=['GET']))
        mapper.connect('/users/{userid}', controller=ctrl,
                       action='get_user', conditions=dict(method=['GET']))
