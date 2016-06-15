# encoding: utf-8

__author__ = 'zj'

from brake.backends import cachebe
from core import baseview


class IpAndAppIdBrake(cachebe.CacheBackend):
    """
    根据ip和设备id 进行访问限制
    """

    def get_ip(self, request):
        ip = request.META.get('HTTP_TRUE_CLIENT_IP', request.META.get('REMOTE_ADDR'))
        device_id = baseview.get_param_from_headers('device-id', request)
        if device_id is None:
            device_id = ''
        return ip + '@' + device_id

