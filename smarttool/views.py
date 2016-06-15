# encoding: utf-8
import logging
import time
import os.path
from django.utils.encoding import force_text, force_bytes
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import StreamingHttpResponse, HttpResponse, FileResponse
from django.http import Http404
import uuid
from core.utils import base_api
from bopianer.settings import WECHAT_APPID, WECHAT_APPSECRET, WECHAT_TOKEN
from django.core.cache import cache
from models import *
from core.baseview import fn_timer
from core import baseview
from django.core.cache import caches
from core.utils import encrypt_utils
import shutil, json
from django.shortcuts import render
import hashlib
from django.template import RequestContext
import sys
import tempfile
from wechat_sdk import WechatConf
from django.http import HttpResponseRedirect
import urllib

# Create your views here.

logger = logging.getLogger(__name__)
conf = WechatConf(

    token=WECHAT_TOKEN,
    appid=WECHAT_APPID,
    appsecret=WECHAT_APPSECRET,
    encrypt_mode='normal',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
    encoding_aes_key='your_encoding_aes_key'  # 如果传入此值则必须保证同时传入 token, appid
)


def wechat_js_check(url):
    jsapi_ticket = conf.jsapi_ticket
    timestamp = create_timestamp()
    noncestr = create_noncestr()
    template = 'jsapi_ticket={0}&noncestr={1}&timestamp={2}&url={3}'.format(jsapi_ticket, noncestr, timestamp, url)

    signature = hashlib.sha1(template).hexdigest()
    return {
        'appid': WECHAT_APPID,
        'timestamp': timestamp,
        'noneStr': noncestr,
        'signature': signature,
    }


def create_timestamp():
    return str(int(time.time()))


def create_noncestr():
    return uuid.uuid4().hex


@require_GET
@base_api.catch
def get_js_ticket(request):
    data = wechat_js_check(request.get_raw_uri())
    return base_api.ok(data)


def redirect_sns(url):
    url = urllib.quote(url, safe='')

    template = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={0}&redirect_uri={' \
               '1}&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'.format(WECHAT_APPID, url)
    return HttpResponseRedirect(template)


def auto_reply(request):
    """
    微信绑定接口
    :param request:
    :return:
    """
    qd = request.GET

    signature = qd.get("signature")
    timestamp = qd.get("timestamp")
    nonce = qd.get("nonce")
    echostr = qd.get("echostr")

    # 首次请求直接返回这个 空串,  验证请求
    if echostr is not None and echostr.strip() != '':
        return HttpResponse(content=echostr, content_type='text/html')

    if signature is None or timestamp is None or nonce is None:
        return HttpResponse(content="failed", content_type='text/html')

    array = [WECHAT_TOKEN, timestamp, nonce]
    array.sort()
    str = ''.join(array)
    signature_server = hashlib.sha1(str).hexdigest()

    if signature == signature_server:
        return HttpResponse(content="", content_type='text/html')

    return HttpResponse(content="failed", content_type='text/html')


def get_openid_by_code(code):
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={0}&secret={1}&code={2}&grant_type' \
          '=authorization_code'.format(WECHAT_APPID, WECHAT_APPSECRET, code)
    data = json.load(urllib.urlopen(url))
    print data
    print data.get('openid')
    return data.get('openid')


@require_GET
@base_api.catch
def index(request):
    """
    小工具首页, 展示拍谱页面
    :param request: 请求
    :return: render一个html
    """
    query_dict = request.GET
    code = query_dict.get('code')
    if code is None or code.strip() == '':
        return redirect_sns(request.get_raw_uri())

    openid = get_openid_by_code(code)
    data = wechat_js_check(request.get_raw_uri())
    data['openid'] = openid
    return render(request, 'index.html', data)


@require_GET
@base_api.catch
def list(request):
    """
    根据openid查询所有的曲谱列表
    :param request:
    :return:
    """
    data = {}
    return render(request, 'list.html', data)


@csrf_exempt
@require_POST
@base_api.catch
def new(request):
    """
    新增曲谱
    :param request:
    :return:
    """
    query_dict = request.POST

    img_media_id = query_dict.get("media_id")
    if img_media_id is None:
        return base_api.error("新增曲谱失败, 没有media_id")

    openid = query_dict.get("openid")
    if openid is None:
        return base_api.error("新增曲谱失败, 没有openid")

    s = Score()
    s.asset_wechat_media_id = img_media_id
    s.date_added = timezone.now()
    s.openid = openid
    s.save()
    # todo 增加一个下载文件的任务
    return base_api.ok({'score_id': s.id})


@csrf_exempt
@require_POST
@base_api.catch
def add_widget(request, score_id):
    count = Score.objects.filter(id__iexact=score_id).count()
    if count == 0:
        logger.warn("找不到对应的曲谱, id:{0}".format(score_id))
        return base_api.error("找不到对应的曲谱, id:{0}".format(score_id))
    query_dict = request.POST

    sw = ScoreWidget()
    sw.score_id = score_id
    sw.top = query_dict.get('top')
    sw.left = query_dict.get('left')
    sw.type = query_dict.get('type')
    sw.content = query_dict.get('content')
    sw.voice_wechat_media_id = query_dict.get('voice_media_id')

    sw.save()
    # todo 增加一个下载文件的任务
    return base_api.ok({'score_widget_id': sw.id})


def download_media(request, media_id):
    if media_id is None or media_id.strip() == '':
        return base_api.error('media_id can not be null')

    access_token = conf.access_token
    url = "http://file.api.weixin.qq.com/cgi-bin/media/get?access_token={1}&media_id={2}".format(access_token, media_id)
