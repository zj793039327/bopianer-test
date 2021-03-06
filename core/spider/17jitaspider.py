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
                title = soup.find('h1',attrs={'class':'ph'})
                songname = str(title.string).split('吉他谱')[0]
                #print title.string
                info = soup.find('em',attrs={'id':'_viewnum'})
                viewnum = info.string
                singer = soup.find('b',attrs={'style':'color:#FF6600;'})
                singername = ''
                if singer:
                    singername = singer.string
                content = soup.find('td',attrs={'id':'article_contents'}).img
                extension = content['src'].split('/')[-1].split('.')[-1]
                scorelist = []
                scorelist.append(content['src'])
                pg = soup.find('div',attrs={'class':'pg'})
                if pg:
                    pagenum = int(re.search('\d+',pg.span.string).group(0))
                    for i in range(2,pagenum+1):
                        scoreurl = '{0}_{1}.html'.format(url[0:-5],str(i))
                        scorecode = self.get(scoreurl)
                        scoresoup = BeautifulSoup(scorecode)
                        scorecontent = scoresoup.find('td',attrs={'id':'article_contents'}).img
                        scorelist.append(scorecontent['src'])
                if not os.path.exists(os.path.join('/home/jixin/Desktop/Resource/17jita/',id)):
                    os.mkdir(os.path.join('/home/jixin/Desktop/Resource/17jita/',id))
                flag = 0
                for item in scorelist:
                    self.download(item,'/home/jixin/Desktop/Resource/17jita/{0}/{1}'.format(id,flag))
                    flag += 1
                flag = 0
                jsontext = {
                    'id':id,
                    'title': title.string,
                    'artist':singername,
                    'score_name':songname,
                    'share_count':viewnum,
                    'extension':extension,
                    'src_from':'17jita'
                }
                print jsontext

                return jsontext
        except Exception as e:
            print e.message


tqb = sooopu()
data = []
for page in range(187,254):
    url = 'http://www.17jita.com/tab/img/index.php?page={0}'.format(str(page))
    pagecode = tqb.get(url)
    if pagecode:
        soup = BeautifulSoup(pagecode)
        try:
            link = soup.find_all('dt',attrs={'class':'xs2'})
            for item in link:
                link_url = 'http://www.17jita.com/{0}'.format(item.a['href'])
                score_info = tqb.savescore(link_url)
                data.append(score_info)
        except Exception,what:
            print what
    with open('/home/jixin/Desktop/Resource/17jita/flag.txt','w') as flag:
        flag.write(str(page))
    with open('/home/jixin/Desktop/Resource/17jita/scorelist2.json','w') as f:
        json.dump(data,f)