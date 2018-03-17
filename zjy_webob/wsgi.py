# coding=utf-8
import json
import six
import logging

import webob
import webob.dec
import webob.exc
import wsgiref.util

from zjy_webob import exception

logger = logging.getLogger(__name__)

class Application(object):

    @classmethod
    def factory(cls, global_config, **local_config):
        return cls(**local_config)

    @webob.dec.wsgify()
    def __call__(self, req):
        """所有controller的入口

        controller会根据routes返回的数据以及HTTP method定位到请求处理函数，
        根据执行结果进行统一的返回数据的格式化处理
        """

        arg_dict = req.environ['wsgiorg.routing_args'][1]
        action = arg_dict.pop('action', None)
        del arg_dict['controller']

        method = req.environ['REQUEST_METHOD'].upper()
        if action is None:
            action = method.lower()
        handler = getattr(self, action)

        logger.info('%(req_method)s %(uri)s', {
            'req_method': method,
            'uri': wsgiref.util.request_uri(req.environ),
        })

        params = arg_dict
        params = self._normalize_dict(params)

        try:
            result = handler(req, **params)
        except exception.Error as e:
            logger.warning(six.text_type(e))
            return render_exception(e, req)
        except Exception as e:
            logger.exception(six.text_type(e))
            return render_exception(exception.ServerError(), req)

        if result is None:
            return render_response(status=(204, 'No Content'))
        elif isinstance(result, six.string_types):
            return result
        elif isinstance(result, webob.Response):
            return result
        elif isinstance(result, webob.exc.WSGIHTTPException):
            return result

        response_code = self.get_response_code(req, action)
        return render_response(body=result, status=response_code)

    def get_client_ip(self, req):
        """获取client的IP

        :type req: :class:`webob.Request`
        """
        clientip = req.environ.get('REMOTE_ADDR')
        if req.headers.get('x-forwarded-for'):
            clientip = req.headers.get('x-forwarded-for').split(',')[0]
        return clientip

    def get_response_code(self, req, action):
        """定义返回的status code

        子类可以不需要关心具体的 `__call__` 如何返回，只需要覆盖该方法，根据
        request和定义的action名称，确定对应的status code，默认创建返回201,
        没有body返回204，其他成功返回200

        :param req: WebOb request
        :param action: routes中定义的action名称
        :rtype: (状态码，消息) 的 tuple
        """
        req_method = req.environ['REQUEST_METHOD']
        code = None
        if req_method == 'POST':
            if action.upper() == req_method:
                code = (201, 'Created')
            else:
                code = (200, 'OK')
        elif req_method == "DELETE":
            code = (204, 'DELETED')
        return code

    def get_requester(self, req):
        userid = req.headers.get('x-daho-user-id', None)
        return userid

    def format_time(self, t):
        """将时间按照固定的UTC格式进行格式化

        如果传入的t为None，返回空字符串
        :type t: `datetime.datetime`
        :rtype: str
        """
        if not t:
            return ''
        fmt = '%Y-%m-%dT%H:%M:%SZ'
        return t.strftime(fmt)

    def _map_columns(self, maps, body):
        """将body中与数据库字段不一致的key转换成数据库字段

        :param maps: 字段映射表，只需要提供不一致的映射列表即可
        :type maps: dict
        :param body: 需要转换的内容
        :type body: dict
        :rtype: 转换后的body
        """
        return {maps.get(k, k): v for (k, v) in body.iteritems()}

    def _invert_dict(self, d):
        """反转字典的key和value"""
        return {v: k for k, v in d.iteritems()}

    def _normalize_arg(self, arg):
        return arg.replace(':', '_').replace('-', '_')

    def _normalize_dict(self, d):
        return {self._normalize_arg(k): v for (k, v) in d.iteritems()}

    def _attribute_is_empty(self, ref, attribute):
        """Check if attribute is empty

        Returns true if the attribute in the given ref (which is a
        dict) is empty or None.
        """
        return ref.get(attribute) is None or ref.get(attribute) == ''

    def _require_attribute(self, ref, attribute):
        """Ensures the reference contains the specified attribute.

        Raise a ValidationError if the given attribute is not present
        """
        if self._attribute_is_empty(ref, attribute):
            msg = '%s field is required and cannot be empty' % attribute
            raise exception.ValidationError(msg)

    def _require_attributes(self, ref, attrs):
        """Ensures the reference contains the specified attributes.

        Raise a ValidationError if any of the given attributes is not present
        """
        missing_attrs = [attribute for attribute in attrs
                         if self._attribute_is_empty(ref, attribute)]

        if missing_attrs:
            msg = '%s field(s) cannot be empty' % ', '.join(missing_attrs)
            raise exception.ValidationError(msg)

    @classmethod
    def base_url(cls, req):
        return req.host_url.rstrip('/')

    def get(self, req):
        """默认action是根据HTTP method来定义，子类需要自行实现"""
        raise exception.MethodNotAllowed(method='GET')

    def post(self, req):
        """默认action是根据HTTP method来定义，子类需要自行实现"""
        raise exception.MethodNotAllowed(method='POST')

    def delete(self, req):
        """默认action是根据HTTP method来定义，子类需要自行实现"""
        raise exception.MethodNotAllowed(method='DELETE')


class Middleware(Application):
    """WSGI middleware基类"""

    @classmethod
    def factory(cls, global_config, **local_config):
        """定义paste.deploy配置文件的paste应用工厂类

        所有paste配置中 ``[filter:APPNAME]`` 配置项的值会以kwargs的形式传入
        ``__init__`` 方法

        常见配置格式如下::

            [filter:analytics]
            redis_host = 127.0.0.1
            paste.filter_factory = keystone.analytics:Analytics.factory

        对应 ``Analytics`` 类的调用方式如下:

        .. code::

            import keystone.analytics
            keystone.analytics.Analytics(app, redis_host='127.0.0.1')

        子类也可以重新实现该方法，不过一般没必要这么做

        """

        def _factory(app):
            return cls(app, **local_config)

        return _factory

    def __init__(self, application):
        super(Middleware, self).__init__()
        self.application = application

    def process_request(self, request):
        """收到请求时调用

        如果返回 `None` ，会继续将请求传入到后面的应用。如果返回相应，请求
        就不再继续下发

        """
        return None

    def process_response(self, request, response):
        """处理返回的消息"""
        return response

    @webob.dec.wsgify()
    def __call__(self, request):
        try:
            response = self.process_request(request)
            if response:
                return response
            response = request.get_response(self.application)
            return self.process_response(request, response)
        except exception.Error as e:
            logger.warning(six.text_type(e))
            return render_exception(e, request)
        except Exception as e:
            logger.exception(six.text_type(e))
            return render_exception(exception.ServerError(), request)


def render_response(body=None, status=None, headers=None):
    """生成WSGI返回消息"""
    headers = [] if headers is None else list(headers)

    if body is None:
        body = ''
        status = status or (204, 'No Content')
    else:
        body = json.dumps(body, encoding='utf-8')
        headers.append(('Content-Type', 'application/json'))
        status = status or (200, 'OK')

    resp = webob.Response(body=body,
                          status='%s %s' % status,
                          headerlist=headers)
    return resp


def render_exception(error, req):
    """生成WSGI的异常返回信息"""

    error_message = error.args[0]

    body = {
        'code': error.code,
        'label': error.label,
        'message': error_message
    }
    if error.level:
        body['level'] = error.level
    headers = []
    status = (error.status_code,
              exception.status_codes.get(error.status_code))
    return render_response(status=status, body=body, headers=headers)
