# coding=utf-8
from __future__ import unicode_literals
import json, re
import sys, os.path, urllib2, cookielib, socket, zlib
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
from time import sleep
import gc

reload(sys)
sys.setdefaultencoding('utf-8')

basepath = '/home/jixin/'


class HttpClient:
    def __init__(self):
        pass


    __cookie = cookielib.CookieJar()
    '''
    代理设置，需要时添加（后续设置为多代理切换）
    __proxy_handler = urllib2.ProxyHandler({"http" : '42.121.6.80:8080'})
    '''
    __req = urllib2.build_opener(urllib2.HTTPCookieProcessor(__cookie))

    __req.add_headers = [
        ('Accept', 'application/javascript, */*;q=0.8'),
        ('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)')
    ]

    urllib2.install_opener(__req)

    def get(self, url, retries=3):
        try:
            req = urllib2.Request(url)
            response = urllib2.urlopen(req, timeout=120)
            html = response.read()
            gzipped = response.headers.get('Content-Encoding')
            if gzipped:
                html = zlib.decompress(html, 16 + zlib.MAX_WBITS)
            return html
        except Exception, what:
            print what
            if retries > 0:
                return self.get(url, retries - 1)
            else:
                print "Get Failed", url
                return ''

    def post(self, url, data):
        try:
            req = urllib2.Request(url, data=data)
            return urllib2.urlopen(req, timeout=120).read()
        except urllib2.HTTPError, e:
            return e.read()
        except socket.timeout, e:
            return ''
        except socket.error, e:
            return ''

    def download(self, url, file):
        try:
            output = open(file, 'wb')
            output.write(urllib2.urlopen(url).read())
            output.close()
        except:
            pass

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



class yuesir(HttpClient):
    def savescore(self,url,shareurl):
        try:
            pagecode = self.get(url)
            if pagecode:
                id = uuid.uuid4().hex
                soup = BeautifulSoup(pagecode)
                title = soup.find('h2',attrs={'class':'page-post-main-top-title'})
                namelist = title.string.split('》')
                artist = namelist[0].split('《')[0]
                score = namelist[0].split('《')[1]
                category = namelist[1]
                #print artist,score,category
                str = self.get(shareurl)
                share_count = json.loads(str[6:-2])['num'][0]
                #print share_count
                download_str = soup.find('div',attrs={'class':'download-info'})
                load_count = download_str.string
                loadlist = re.findall('\d+',load_count)
                download_count = loadlist[0]
                filelength = loadlist[1]
                content = soup.find('div','page-post-show-download-main-item-button')
                download_url = content.a['url']
                print download_url
                extension = download_url.split('/')[-1].split('.')[-1]
                self.download(download_url,os.path.join('/home/jixin/yuesir','{0}.{1}'.format(id,extension)))
                return {
                    'id':id,
                    'artist':artist,
                    'score_name':score,
                    'category':category,
                    'share_count':share_count,
                    'download_count':download_count,
                    'filelength':filelength,
                    'download_url':download_url,
                    'extension':extension,
                    'src_from':'yuesir'
                }
        except Exception as e:
            print e.message
tqb = yuesir()
data = []
for i in range(8001,8249):
    url = 'http://www.yuesir.com/ipu/{0}.html'.format(str(i))
    shareurl = 'http://api.share.baidu.com/getnum?url=http%3A%2F%2Fwww.yuesir.com%2Fipu%2F{0}.html&callback=count'.format(i)
    data.append(tqb.savescore(url,shareurl))
with open('/home/jixin/yuesir/scorelist9.json','w') as f:
    json.dump(data,f)