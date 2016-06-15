# encoding: utf-8
__author__ = 'zjhome'

import time
from functools import wraps
from bopianer import settings
from urllib import unquote
from django.core.cache import caches
import oss2
import uuid
import hashlib
import base64
from core.utils import base_api


def fn_timer(function):
    """
     prints costs time for every function
    :param function:
    :return:
    """

    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" % (function.func_name, str(t1 - t0)))
        return result

    return function_timer


def get_ip(request):
    """
    查询ip
    :param request:
    :return:
    """
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip


def get_param_from_headers(param_name, request):
    """
    从 header 获取参数, 参数 之间 不能有下划线, 只能有连字符
    :param param_name:
    :param request:
    :return:
    """
    s = param_name.replace('-', '_')
    s = s.upper()
    return request.META.get('HTTP_' + s)


def get_cover_pic_url(cover_pic_url, thumb_type='MID'):
    """
    获取不同大小封面图片的地址
    """
    if settings.COVER_IMAGE_OSS_THUMB.get(thumb_type) is None:
        raise 'could not find the thumb type {0} in settings'.format(thumb_type)
    return settings.COVER_IMAGE_OSS_THUMB.get(thumb_type).format(settings.OSS_BUCKET.get('pic_bucket'), cover_pic_url)


def read_from_cache(key):
    cache = caches['default']
    value = cache.get(key)
    return value
def write_to_cache(key, value):
    cache = caches['default']
    cache.set(key, value, settings.NEVER_REDIS_TIMEOUT)

def save_share_asset(path,object_name):
    with open(path, 'rb') as b:
        # upload to aliyun oss
        key = settings.ACCESS_KEY_ID
        key_sec = settings.ACCESS_KEY_SECRET
        auth = oss2.Auth(key, key_sec)
        bucket = settings.OSS_BUCKET.get('pic_bucket')
        print bucket
        endpoint = settings.END_POINT
        try:
            service = oss2.Bucket(auth, 'http://' + endpoint, bucket)
            print object_name,service
            service.put_object(object_name, b)
        except Exception as e:
            print 'xx'
            print e

def download_token(request):
    device_id = get_param_from_headers('device-id', request)
    query_dict = request.POST
    if query_dict.get('key') is not None:
        key = query_dict.get('key')
    else:
        return False
    if query_dict.get('timestamp') is not None:
        timestamp = query_dict.get('timestamp')
    else:
        return False
    if query_dict.get('dtoken') is not None:
        dtoken = query_dict.get('dtoken')
    else:
        return False
    try:
        device = Device.objects.get(device_id__iexact=device_id)
    except Device.DoesNotExist:
        return False
    token_str = '{0}{1}{2}{3}'.format(device.device_unique_tag,key,timestamp,'letz33245')
    encode_str = base64.encodestring(token_str)
    md_str = _get_MD5_value(encode_str)
    token = _get_SHA_value(md_str)

    if dtoken == token:
        return True
    else:
        return False


def _get_MD5_value(src):
    md = hashlib.md5()
    md.update(str)
    md_digest = md.hexdigest()
    return md_digest
def _get_SHA_value(src):
    sha1 = hashlib.sha1()
    sha1.update(src)
    sha1_digest = sha1.hexdigest()
    return sha1_digest