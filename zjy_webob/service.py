# coding=utf-8
from zjy_webob.routers import Version, ComposingRouter
import zjy_webob.user.routers as user


def add_routers(modules):
    # router must be of type smartcontrol.wsgi.ComposableRouter
    return [m.Router() for m in modules]


def version_app_factory(global_cfg, **local_cfg):
    modules = [user]
    sub_routers = add_routers(modules)
    sub_routers.append(Version())
    return ComposingRouter(routers=sub_routers)
