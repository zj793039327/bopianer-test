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
                listtitle = soup.find('div',attrs={'class':'listltitle'})
                title = listtitle.h1.string
                print title
                songname = str(title.string).split('吉他谱')[0]
                singer = listtitle.find('span',attrs={'class':'spanimg1'}).string.split('：')[-1]
                aid = url.split('/')[-1].split('.')[0]
                viewtxt = self.get('http://www.jitaba.cn/plus/count.php?view=yes&aid={0}&mid=1'.format(aid))
                viewnum = re.search('\d+',viewtxt).group(0)
                content = soup.find('div',attrs={'id':'tabzone'})
                imgs = content.find_all('img')
                flag = 0
                extension = 'jpg'
                if not os.path.exists(os.path.join('/home/jixin/Desktop/Resource/jitaba/',id)):
                    os.mkdir(os.path.join('/home/jixin/Desktop/Resource/jitaba/',id))
                for item in imgs:
                    imgurl = item['src']
                    self.download(imgurl,'/home/jixin/Desktop/Resource/jitaba/{0}/{1}'.format(id,flag))
                    flag += 1
                    extension = imgurl.split('/')[-1].split('.')[-1]

                jsontext = {
                    'id':id,
                    'title': title,
                    'artist':singer,
                    'score_name':songname,
                    'share_count':viewnum,
                    'extension':extension,
                    'src_from':'jitaba'
                }
                return jsontext
        except Exception as e:
            print e.message
    def savescore2(self,url,title,artist):
        try:
            pagecode = self.get(url)
            if pagecode:
                id = uuid.uuid4().hex
                soup = BeautifulSoup(pagecode)
                songname = str(title.string).split('吉他谱')[0]
                aid = url.split('/')[-1].split('.')[0]
                viewtxt = self.get('http://www.jitaba.cn/plus/count.php?view=yes&aid={0}&mid=1'.format(aid))
                viewnum = re.search('\d+',viewtxt).group(0)
                content = soup.find('span',attrs={'class':'STYLE1'})
                #print content
                imgs = content.find_all('img')
                print imgs
                flag = 0
                extension = 'jpg'
                if not os.path.exists(os.path.join('/home/jixin/Desktop/Resource/jitaba/',id)):
                    os.mkdir(os.path.join('/home/jixin/Desktop/Resource/jitaba/',id))
                for item in imgs:
                    imgurl = 'http://www.jitaba.cn{0}'.format(item['src'])
                    self.download(imgurl,'/home/jixin/Desktop/Resource/jitaba/{0}/{1}'.format(id,flag))
                    flag += 1
                    extension = imgurl.split('/')[-1].split('.')[-1]

                jsontext = {
                    'id':id,
                    'title': title,
                    'artist':artist,
                    'score_name':songname,
                    'share_count':viewnum,
                    'extension':extension,
                    'src_from':'jitaba'
                }
                return jsontext
        except Exception as e:
            print e.message


tqb = sooopu()
data = []
for page in range(127,243):
    url = 'http://www.jitaba.cn/jitapu/list_41_{0}.html'.format(str(page))
    pagecode = tqb.get(url)
    if pagecode:
        soup = BeautifulSoup(pagecode)
        try:
            link = soup.find_all('td',attrs={'width':'98%'})
            for item in link:
                try:
                    item_name = item.find('a',attrs={'class':'STYLE3'})
                    link_url = item_name['href']
                    song_name = item_name.string
                    singer = item.find('div',attrs={'align':'center'}).a.string
                    score_info = tqb.savescore2(link_url,song_name,singer)
                    data.append(score_info)
                except:
                    pass
        except Exception,what:
            print what
    with open('/home/jixin/Desktop/Resource/jitaba/flag.txt','w') as flag:
        flag.write(str(page))
    with open('/home/jixin/Desktop/Resource/jitaba/scorelist3.json','w') as f:
        json.dump(data,f)