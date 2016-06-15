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
                songname = title
                if '(' in songname:
                    songname = songname.split('(')[0]
                if '（' in songname:
                    songname = songname.split('（')[0]
                print songname
                viewtxt = soup.find('div',attrs={'class':'mt0'})
                viewtxt = viewtxt.small.string
                viewnum = re.search('\d+',viewtxt).group(0)
                content = soup.find('div',attrs={'id':'picdiv'})
                imgs = content.find_all('img')
                flag = 0
                extension = 'jpg'
                if not os.path.exists(os.path.join('/home/jixin/Desktop/Resource/91jita/',id)):
                    os.mkdir(os.path.join('/home/jixin/Desktop/Resource/91jita/',id))
                for item in imgs:
                    imgurl = item['src']
                    self.download(imgurl,'/home/jixin/Desktop/Resource/91jita/{0}/{1}'.format(id,flag))
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
with open('/home/jixin/Desktop/Resource/91jita/artisturl2.json','r') as f:
    jsonobj = json.load(f)
    for item in jsonobj:
        artist = item.get('artist')
        linkurl = item.get('artist_url')
        pagecode = tqb.get(linkurl)
        if pagecode:
            soup = BeautifulSoup(pagecode)
            try:
                pagenum = soup.find('div',attrs={'id':'datatable_paginate'})
                num = re.findall('\d+', str(pagenum))[1]
                if num > 0:
                    for i in range(1,int(num)+1):
                        url = "{0}/{1}/1".format(linkurl[0:-4],str(i))
                        print url
                        scorepage = tqb.get(url)
                        scoresoup = BeautifulSoup(scorepage)
                        scorelist = scoresoup.find_all('td',attrs={'class':'email-subject'})
                        for item in scorelist:
                            try:
                                score_name = item.a.string
                                score_url = item.a['href']
                                score_info = tqb.savescore2(score_url,score_name,artist)
                                data.append(score_info)
                            except:
                                pass
            except Exception,what:
                print what
        with open('/home/jixin/Desktop/Resource/91jita/flag.txt','w') as flag:
            flag.write(linkurl)
        with open('/home/jixin/Desktop/Resource/91jita/scorelist2.json','w') as f:
                json.dump(data,f)
"""
searchlist = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
for page in searchlist:
    url = 'http://www.91jitapu.com/searchbypinyin/{0}'.format(page)
    pagecode = tqb.get(url)
    if pagecode:
        soup = BeautifulSoup(pagecode)
        try:
            link = soup.find_all('td',attrs={'class':'email-subject'})
            for item in link:
                try:
                    artist = item.a.string
                    artist_url = item.a['href'].replace('-1','1')
                    print artist,artist_url
                    data.append({
                        'artist':artist,
                        'artist_url':artist_url
                    })
                except:
                    pass
        except Exception,what:
            print what
print 'over'
with open('/home/jixin/Desktop/Resource/91jita/artisturl.json','w') as f:
    json.dump(data,f)
"""