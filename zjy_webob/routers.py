# coding=utf-8
import routes
from routes.middleware import RoutesMiddleware
import webob.dec

from zjy_webob import exception
from zjy_webob.controllers import VersionController
from zjy_webob.wsgi import render_exception


class Router(object):
    """将请求映射到对应WSGI应用的middleware"""

    def __init__(self, mapper):
        """根据指定mapper返回对应的router

        每个 ``mapper`` 的route都必须指定一个 ``controller`` 的WSGI应用，
        同时可以指定 ``action`` 将请求转到对应的处理方法。

        示例代码:

        .. code::

          mapper = routes.Mapper()
          sc = ServerController()

          # Explicit mapping of one route to a controller+action
          mapper.connect(None, '/svrlist', controller=sc, action='list')

          # Actions are all implicitly defined
          mapper.resource('server', 'servers', controller=sc)

          # Pointing to an arbitrary WSGI app.  You can specify the
          # {path_info:.*} parameter so the target app can be handed just that
          # section of the URL.
          mapper.connect(None, '/v1.0/{path_info:.*}', controller=BlogApp())

        """
        self.mapper = mapper
        self._router = RoutesMiddleware(self._dispatch, self.mapper)

    @webob.dec.wsgify()
    def __call__(self, req):
        """将请求转到 ``self.mapper`` 对应的 ``controller``

        如果没找到，返回404

        """
        return self._router

    @staticmethod
    @webob.dec.wsgify()
    def _dispatch(req):
        """实际转发到 ``controller`` 的处理逻辑

        由 ``self._router``  转发请求并将一些routes相关信息写入 ``req.environ``

        """
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            return render_exception(exception.NotFound(), req)
        app = match['controller']
        return app


class ComposingRouter(Router):
    """基于多个ComposableRouters生成router"""

    def __init__(self, mapper=None, routers=None):
        if mapper is None:
            mapper = routes.Mapper()
        if routers is None:
            routers = []
        for router in routers:
            router.add_routes(mapper)
        super(ComposingRouter, self).__init__(mapper)


class ComposableRouter(Router):
    """ComposingRouter的组件"""

    def __init__(self, mapper=None):
        if mapper is None:
            mapper = routes.Mapper()
        self.add_routes(mapper)
        super(ComposableRouter, self).__init__(mapper)

    def add_routes(self, mapper):
        """添加route信息到指定mapper"""
        pass


class Version(ComposableRouter):

    def add_routes(self, mapper):
        ctrl = VersionController()
        mapper.connect('/', controller=ctrl)
        mapper.connect('/versions', controller=ctrl,
                       action='get_zjy_webob_version')
