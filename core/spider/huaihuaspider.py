# coding=utf-8
from __future__ import unicode_literals
import json, re
import sys, os.path, urllib2, cookielib, socket, zlib
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
from Queue import Queue
from time import sleep

reload(sys)
sys.setdefaultencoding('utf-8')


class HttpClient:
    def __init__(self):
        pass


    __cookie = cookielib.CookieJar()
    # 代理设置，需要时添加（后续设置为多代理切换）
    __proxy_handler = urllib2.ProxyHandler({"http" : '124.207.175.91:8080'})

    __req = urllib2.build_opener(urllib2.HTTPCookieProcessor(__cookie))#,__proxy_handler)

    __req.add_headers = [
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
        ('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'),
        ('Host','www.xdukulele.com'),
    ]

    urllib2.install_opener(__req)

    def get(self, url, retries=3):
        try:
            req = urllib2.Request(url)
            response = urllib2.urlopen(req, timeout=12)
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



class xdukulele(HttpClient):
    def savescore(self,url,id):
        try:
            print url
            pagecode = self.get(url)
            if pagecode:
                soup = BeautifulSoup(pagecode)
                share_count = soup.find('span', attrs={'class':'xi1'}).string
                if not os.path.exists(os.path.join('/home/jixin/xdukulele/',id)):
                    os.mkdir(os.path.join('/home/jixin/xdukulele/',id))
                info = soup.find('td',attrs={'class':'t_f'})
                flag = 0
                extension = 'gif'
                imgs = info.find_all('img')
                print imgs
                for i in imgs:
                    down_url = 'http://xdukulele.com/{0}'.format(i['file'])
                    print down_url
                    #print '/home/jixin/xdukulele/{0}/{1}'.format(id,flag)
                    self.download(down_url, '/home/jixin/xdukulele/{0}/{1}'.format(id,flag))
                    extension = i['file'].split('.')[-1]
                    flag += 1
                flag = 0

                return share_count,extension
        except Exception as e:
            print e.message


tqb = xdukulele()
data = []
for page in range(1,7):
    url = 'http://xdukulele.com/forum.php?mod=forumdisplay&fid=43&page={0}'.format(str(page))
    #print url
    pagecode = tqb.get(url)
    if pagecode:
        soup = BeautifulSoup(pagecode)
        try:
            link = soup.find_all('th',attrs={'class':'common'})
            for item in link:
                id = uuid.uuid4().hex
                if item.em is not None:
                    type = item.em.a.string
                else:
                    type = ''
                info = item.find('a',attrs={'class':'s xst'})
                print info
                infolist = re.split('-|－',info.string)
                if len(infolist) > 2:
                    artist = infolist[1]
                    song_name = infolist[0]
                    desc = infolist[2]
                else:
                    artist = ''
                    song_name = infolist[0]
                    desc = infolist[1]
                link_url = 'http://xdukulele.com/{0}'.format(info['href'])
                share_count,extension = tqb.savescore(link_url, id)
                data.append({
                    'id':id,
                    'artist':artist,
                    'score_name':song_name,
                    'category':type,
                    'share_count':share_count,
                    'extension':extension,
                    'src_from':'xdukulele'
                })
        except Exception,what:
            print what
    with open('/home/jixin/xdukulele/flag.txt','w') as flag:
        flag.write(str(page))
    with open('/home/jixin/xdukulele/scorelist.json','w') as f:
        json.dump(data,f)