# coding=utf-8
import zjy_webob
from zjy_webob.wsgi import Application


class VersionController(Application):

    def _get_url(self, req, version):
        url = self.base_url(req)
        return '{}/{}/'.format(url, version)

    def get_version_v2(self, req):
        version = {
            'id': '2.0',
            'status': 'CURRENT',
            'links': {
                'ref': 'self',
                'href': self._get_url(req, 'v2')
            }
        }
        return {'version': version}

    def get(self, req):
        versions = []
        # Do not expose version 1 API until explicitly requested.
        # Leave it for internal use only
        v2_version = self.get_version_v2(req)
        versions.append(v2_version.get('version', {}))
        return {'versions': versions}

    def get_zjy_webob_version(self, req):
        version = [{
            'module': 'zjy_webob',
            'id': zjy_webob.__version__ or ''
        }]
        return {'versions': version}
