# encoding: utf-8

__author__ = 'zjhome'
import logging
import os
import os.path
import urllib2
import cookielib
import socket
import zlib
import time
from socket import error as SocketError
from threading import Thread
from Queue import Queue

from django.utils import timezone

from system.models import AssetPhysical
from youpua_server.settings import MEDIA_ROOT
from core.business_error import BusinessError
from youpua_server.settings import MUSIC_BRAINZ


if __name__ == '__builtin__':
    logger = logging.getLogger('core.migrate.download_pic')
else:
    logger = logging.getLogger(__name__)


class HttpClient:
    def __init__(self):
        pass


    __cookie = cookielib.CookieJar()
    '''
    代理设置，需要时添加（后续设置为多代理切换）'''
    __proxy_handler = urllib2.ProxyHandler({"http" : '127.0.0.1:1080'})

    __req = urllib2.build_opener(urllib2.HTTPCookieProcessor(__cookie))
    __req.add_headers = [
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
        ('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)')
    ]

    urllib2.install_opener(__req)

    def get(self, url, headers, retries=3):
        try:
            req = urllib2.Request(url, headers=headers)
            response = urllib2.urlopen(req, timeout=120)
            html = response.read()
            gzipped = response.headers.get('Content-Encoding')
            if gzipped:
                html = zlib.decompress(html, 16 + zlib.MAX_WBITS)
            return html
        except Exception, what:
            print what
            if retries > 0:
                return self.get(url, headers, retries - 1)
            else:
                print "Get Failed", url
                return ' '

    def post(self, url, data, headers):
        try:
            req = urllib2.Request(url, data=data, headers=headers)
            return urllib2.urlopen(req, timeout=120).read()
        except urllib2.HTTPError, e:
            return e.read()
        except socket.timeout, e:
            return ''
        except socket.error, e:
            return ''

    def download(self, url, file):
        try:
            # print url
            output = open(file, 'wb')
            output.write(urllib2.urlopen(url, timeout=15).read())
            output.close()
        except urllib2.URLError as e:
            print e
            logger.error(e)
            raise BusinessError(e)
        except SocketError as e:
            logger.error(e)
            print e
            raise BusinessError(e)
        except ValueError as e:
            logger.error(e)
            print e
            raise BusinessError(e)


    def get_cookies(self, key):
        for c in self.__cookie:
            if c.name == key:
                return c.value
        return ''

    def set_cookie(self, key, val, domain):
        ck = cookielib.Cookie(version=0, name=key, value=val, port=None, port_specified=False, domain=domain,
                              domain_specified=False, domain_initial_dot=False, path='/', path_specified=True,
                              secure=False, expires=None, discard=True, comment=None, comment_url=None,
                              rest={'HttpOnly': None}, rfc2109=False)
        self.__cookie.set_cookie(ck)

q = Queue()

def download_img():
    assets = AssetPhysical.objects.filter(local_path__exact='')
    D = downloadImage()
    counter = len(assets)
    print len(assets)
    for asset in assets:
        counter = counter - 1
        if asset.extension == '*':
            continue

        q.put(asset)
    q.join()

       #do_download(asset, counter)


def do_download(asset, counter):
    local_path = 'pic_content/{0}/{1}'.format(asset.id[0], asset.id[1], asset.id,
                                              asset.extension)
    if not os.path.exists(MEDIA_ROOT + local_path):
        os.makedirs(MEDIA_ROOT + local_path)
    local_file_name = '{0}/{1}.{2}'.format(local_path, asset.id, asset.extension)
    try:
        print asset.remote_url + str(timezone.localtime(timezone.now()))
        D.downloadpic(asset.remote_url, MEDIA_ROOT + local_file_name)
        asset.local_path = local_file_name
        asset.byte_size = os.path.getsize(MEDIA_ROOT + local_file_name)
        asset.date_download = timezone.now()
        asset.save()
        print '{1}  saved img {0}'.format(MEDIA_ROOT + local_file_name, counter)
    except BusinessError as e:
        logger.error(e)
        return


class downloadImage(HttpClient):
    def downloadpic(self, url, file):
        try:
            self.download(url, file)
        except BusinessError as e:
            logger.error(e)
            raise BusinessError('download pic error, ' + url)


D = downloadImage()



####################
# build to a async task
def worker():
    while True:
        raw = q.get()
        counter = q.qsize()
        do_download(raw, counter)
        q.task_done()



for i in range(3):
    t = Thread(target=worker)
    t.daemon = True
    t.start()

download_img()