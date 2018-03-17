# coding=utf-8
import sys
import inspect
import logging

logger = logging.getLogger(__name__)

status_codes = {
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    204: 'No Content',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    304: 'Not Modified',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    409: 'Conflict',
    429: 'Too Many Requests',
    500: 'Internal Server Error',
}

DEBUG = 'DEBUG'
INFO = 'INFO'
WARNING = 'WARNING'
ERROR = 'ERROR'
CRITICAL = 'CRITICAL'


class Error(Exception):
    code = None
    label = None
    msg_format = None
    level = None

    def __init__(self, msg=None, level=None, **kwargs):
        if not msg:
            try:
                msg = self.msg_format % kwargs
            except Exception as e:
                logger.exception(unicode(e))
                msg = self.msg_format or ''
        self.level = level
        super(Error, self).__init__(msg)


class ClientError(Error):
    status_code = 400


class AuthenticationError(ClientError):
    status_code = 401
    code = 1005
    label = "AUTHENTICATION_FAILURE"
    msg_format = "Authentication failed"


class RequestForbidden(ClientError):
    status_code = 403
    code = 1023
    label = "REQUEST_FORBIDDEN"
    msg_format = "Request forbidden"


class InvalidUserError(ClientError):
    status_code = 403
    code = 1003
    label = 'USER_NOT_RECOGNIZED'
    msg_format = "User with ID %(userid)s not found"


class NotFound(Error):
    status_code = 404
    code = 1000
    label = "NOT_FOUND"
    msg_format = "Resource not found"


class MethodNotAllowed(ClientError):
    status_code = 405
    code = 1015
    label = "METHOD_NOT_ALLOWED"
    msg_format = "Method %(method)s not allowed"


class ServerError(Error):
    status_code = 500
    label = 'SERVER_ERROR'
    msg_format = "Internal Server Error"


class ValidationError(ClientError):
    code = 1014
    label = "VALIDATION_FAILURE"
    msg_format = "Request validation failure"


def get_code_exceptions():
    code_exceptions = dict()
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            if issubclass(obj, Error):
                code_exceptions[obj.label] = obj
    return code_exceptions
