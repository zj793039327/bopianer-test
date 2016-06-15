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
    def savescore(self,url,scorename,title,singer):
        try:
            pagecode = self.get(url)
            if pagecode:
                id = uuid.uuid4().hex
                soup = BeautifulSoup(pagecode)
                #listtitle = soup.find('fieldset',attrs={'id':'tabinfo'})

                viewtxt = soup.find('span', attrs={'id':'collectionnumber'})
                viewnum = viewtxt.string
                print viewnum
                content = soup.find('div',attrs={'class':'imgtab'})
                imgs = content.find_all('img')
                flag = 0
                extension = 'jpg'
                if not os.path.exists(os.path.join('/home/jixin/Desktop/Resource/jitashe/',id)):
                    os.mkdir(os.path.join('/home/jixin/Desktop/Resource/jitashe/',id))
                for item in imgs:
                    imgurl = 'http://www.jitashe.net/{0}'.format(item['zoomfile'])
                    print imgurl
                    self.download(imgurl,'/home/jixin/Desktop/Resource/jitashe/{0}/{1}'.format(id,flag))
                    flag += 1
                    extension = imgurl.split('/')[-1].split('.')[-1]

                jsontext = {
                    'id':id,
                    'title': title,
                    'artist':singer,
                    'score_name':scorename,
                    'share_count':viewnum,
                    'extension':extension,
                    'src_from':'jitashe'
                }
                return jsontext
        except Exception as e:
            print e.message


tqb = sooopu()
data = []
with open('/home/jixin/Desktop/Resource/jitashe/artistlist.json','r') as f:
    jsonobj = json.load(f)
    for item in jsonobj:
        linkurl = item.get('artist_url')
        pagecode = tqb.get(linkurl)
        if pagecode:
            soup = BeautifulSoup(pagecode)
            try:
                pagenum = soup.find('td',attrs={'class':'ptm'})
                num = re.search('\d+', pagenum.span.string).group(0)
                singerbq = soup.find('div',attrs={'class':'z'})
                #print singerbq
                singer_a = singerbq.find_all('a')[3]
                singer = singer_a.string
                #print singer
                for i in range(1,int(num)+1):
                    pageurl = '{0}{1}/'.format(linkurl,str(i))
                    precode = tqb.get(pageurl)
                    presoup = BeautifulSoup(precode)
                    scorelist = presoup.find_all('tr',attrs={'class':'plhin'})
                    for item in scorelist:
                        info = item.span.a
                        scorename = info.string
                        scoreurl = 'http://www.jitashe.net{0}'.format(info['href'])
                        #print scorename,scoreurl
                        bq = item.find('span',attrs={'class':'tablist_tags hin'})
                        title = ''
                        if bq:
                            for b in bq.find_all('a'):
                                title += b.string
                        #print title
                        score_info = tqb.savescore(scoreurl,scorename,title,singer)
                        data.append(score_info)
            except Exception,what:
                print what
        with open('/home/jixin/Desktop/Resource/jitashe/flag.txt','w') as flag:
            flag.write(linkurl)
        with open('/home/jixin/Desktop/Resource/jitashe/scorelist1.json','w') as f:
                json.dump(data,f)


"""
for page in range(1,243):
    url = 'http://www.jitaba.cn/jitapu/list_41_{0}.html'.format(str(page))
    pagecode = tqb.get(url)
    if pagecode:
        soup = BeautifulSoup(pagecode)
        try:
            link = soup.find_all('a',attrs={'class':'STYLE3'})
            for item in link:
                try:
                    link_url = item['href']
                    score_info = tqb.savescore(link_url)
                    data.append(score_info)
                except:
                    pass
        except Exception,what:
            print what
    with open('/home/jixin/Desktop/Resource/jitaba/flag.txt','w') as flag:
        flag.write(str(page))
    with open('/home/jixin/Desktop/Resource/jitaba/scorelist2.json','w') as f:
        json.dump(data,f)
"""