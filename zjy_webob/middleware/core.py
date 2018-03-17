# coding=utf-8
from zjy_webob.wsgi import Middleware


class CookieAuthMiddleware(Middleware):
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        return response


class AccessKeyAuthMiddleware(Middleware):
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        return response


class InternalServiceAuthMiddleware(Middleware):
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        return response


class SysLogMiddleware(Middleware):
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        return response


class PagingMiddleware(Middleware):
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        return response


class ResourceMiddleware(Middleware):
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        return response
