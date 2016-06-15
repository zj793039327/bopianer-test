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
        ('Host','www.sooopu.com'),
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



class sooopu(HttpClient):
    def savescore(self,url):
        try:
            pagecode = self.get(url)
            if pagecode:
                id = uuid.uuid4().hex
                soup = BeautifulSoup(pagecode)
                title = soup.find('h1',attrs={'class':'title'}).string.rstrip()
                #print title.string
                info = soup.find('div',attrs={'class':'info2'})
                #print info
                pattern = re.compile('<div class="info2">.*?[.\n]+.*?</strong>(.*?)[.\n]+<strong>.*?</strong>(.*?)[.\n]+<strong>.*?</strong>(.*?)[.\n]+<strong>.*?</strong>(.*?)[.\n]+<strong>.*?</strong>(.*?)[.\n]+<strong>.*?[.\n]+</div>',re.S)
                m = re.search(pattern,str(info))
                if m is not None:
                    if "演唱者" in str(info):
                        artist = m.group(1).rstrip()
                        category = m.group(2).rstrip()
                        tab = m.group(3).rstrip()
                        d_added = m.group(5).rstrip()
                    else:
                        artist = ''
                        category = m.group(1).rstrip()
                        tab = m.group(2).rstrip()
                        d_added = m.group(4).rstrip()
                else:
                    artist = ''
                    category = ''
                    tab = ''
                    d_added = ''
                score_id = url.split('/')[-1].split('.')[0]
                clickurl = 'http://www.sooopu.com/js/clicks.asp?id={0}'.format(score_id)
                result = self.get(clickurl)
                search_count = re.search('\d+',result)
                if search_count is not None:
                    share_count = search_count.group()
                else:
                    share_count = 0
                content = soup.find('div',attrs={'class','content'})
                pattern = re.compile('<img.*?src="(.*?)"',re.S)
                imgs = re.findall(pattern,str(content))
                if not os.path.exists(os.path.join('/home/jixin/sooopu/',id)):
                    os.mkdir(os.path.join('/home/jixin/sooopu/',id))
                flag = 0
                extension = 'gif'
                for i in imgs:
                    down_url = 'http://www.sooopu.com{0}'.format(i)
                    print down_url
                    #print '/home/jixin/sooopu/{0}/{1}'.format(id,flag)
                    self.download(down_url, '/home/jixin/sooopu/{0}/{1}'.format(id,flag))
                    extension = i.split('.')[-1]
                    flag += 1
                flag = 0

                jsontext = {
                    'id':id,
                    'artist':artist,
                    'score_name':title,
                    'category':category,
                    'share_count':share_count,
                    'extension':extension,
                    'src_from':'sooopu'

                }
                print jsontext
                return jsontext
        except Exception as e:
            print e.message


tqb = sooopu()
data = []
for page in range(539,576):
    url = 'http://www.sooopu.com/JitaPu/index{0}.html'.format(str(page))
    pagecode = tqb.get(url)
    if pagecode:
        soup = BeautifulSoup(pagecode)
        try:
            link = soup.find_all('td',attrs={'class':'t_title cb'})
            for item in link:
                link_url = 'http://www.sooopu.com{0}'.format(item.a['href'])
                score_info = tqb.savescore(link_url)
                data.append(score_info)
        except Exception,what:
            print what
    with open('/home/jixin/sooopu/flag.txt','w') as flag:
        flag.write(str(page))
    with open('/home/jixin/sooopu/scorelist.json','w') as f:
        json.dump(data,f)