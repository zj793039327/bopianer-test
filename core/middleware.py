# encoding:utf-8
__author__ = 'zjhome'
from django.core.cache import caches
from django.http import HttpResponse
from django.utils import timezone
from system.models import Device
import logging
import json
from youpua_server.settings import APP_TOKEN_EXPIRE_SECONDS
from core import baseview


def error(error_msg, status):
    logger = logging.getLogger('django')
    logger.error("error " + error_msg)
    resp = {
        'status': status,
        'message': 'request is not valid',
        'data': error_msg
    }
    return HttpResponse(content=json.dumps(resp), status=403,
                        content_type='application/json')


class AppCheckMiddleware(object):
    """
    校验请求使用的middleware
    """

    def __init__(self):
        pass

    def process_request(self, request):
        """
        检测 request 的 头中 是否有 对应的字段
        :param request:
        :return:
        """
        if not request.path.startswith(u'/api'):
            return None

        cache = caches['device_tokens']
        token = baseview.get_param_from_headers('youpua-token', request)
        device_id = baseview.get_param_from_headers('device-id', request)
        if device_id is None:
            return error('request is not from app', 10)
        server_token = cache.get(device_id)
        if server_token is None:
            if Device.objects.filter(app_id__iexact=device_id).count() > 0:
                # 已经注册 但是没有token, 直接提示刷新token
                return error('app token is expired', 11)
            else:
                # 未注册
                return None
        else:
            if server_token == token:
                return None
            else:
                return error('check token failed', 12)
                # 此处只进行redis的验证, 不进行数据库的认证
                # if server_token is None:
                # return error('app token is expired', 11)
                # else:
                # if device is not None and device.token_expire_time is not None:
                # dt = device.token_expire_time
                # now = timezone.now()
                # expire_seconds = (dt - now).seconds
                # if expire_seconds <= 0:
                #             return error('app token is expired', 11)
                #     else:
                #         expire_seconds = APP_TOKEN_EXPIRE_SECONDS
                #
                #     cache.set(device_id, token, timeout=expire_seconds)
                #     if server_token == token:
                #         return None
                #     else:
                #         return error('check token failed', 12)




