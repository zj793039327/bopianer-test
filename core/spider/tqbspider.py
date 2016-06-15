# coding=utf-8
from __future__ import unicode_literals
import json, re
import sys, os.path, urllib2, cookielib, socket, zlib
from rds.models import *
from bs4 import BeautifulSoup
from datetime import datetime


reload(sys)
sys.setdefaultencoding('utf-8')

basepath = '/home/daohaoisbibi/'


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
                return ' '

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


failedlist = []
count = 0


class tanqinba(HttpClient):
    def getInfo(self, song):
        try:
            url = 'http://www.tan8.com/jitapu-' + song['song_id'] + '.html'
            #global count
            #count += 1
            #print count
            pagecode = self.get(url)
            if pagecode:
                soup = BeautifulSoup(pagecode)
                # get yuepu
                content = soup.find('div', 'jita_yuepu_introduce')
                pattern = re.compile(
                    '<div.*?img">.*?src="(.*?)" width.*?<span>(.*?)</span>.*?<span>(.*?)</span>.*?<span>(.*?)</span>.*?<span>(.*?)</span>.*?<p.*?content_color">(.*?)</p>',
                    re.S)
                yuepu = re.search(pattern, str(content))
                c_score_id = uuid.uuid4().hex
                if yuepu:
                    #print 'get yuepu'
                    c_artist_name = yuepu.group(2).encode('utf-8')
                    c_name = song['song_name'].encode('utf-8')
                    c_desc = yuepu.group(6)
                    c_src_from = "Tan8"
                    n_count_view = yuepu.group(4)
                    d_added=datetime.now()
                    d_modified = datetime.now()
                    content = soup.find('i', id='comments_count_num')
                    liuyannum = re.search('\d', str(content))
                    #本地寻找乐谱文件

                    savepath = os.path.join(basepath,'DB_FILE/{0}/{1}/'.format(c_score_id[0],c_score_id[1]))
                    if not os.path.exists(savepath):
                        print savepath
                        os.makedirs(savepath)

                    flag = self.mvgtpfiles(song, os.path.join(basepath, 'DB_FILE/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id)), c_artist_name)
                    if flag:
                        ts = TRawScore(c_score_id=c_score_id, c_artist_name=c_artist_name, c_name=c_name,
                                   c_desc=c_desc, c_src_from=c_src_from,d_added=d_added,d_modified=d_modified,n_count_view=n_count_view)
                        ts.save(using='rds')

                        print c_score_id
                    #self.download(yuepu.group(1),
                    #              os.path.join(basepath, 'score_content/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id)))
                    #本地寻找乐谱文件
                    #print 'mv file'
                    #self.mvgtpfiles(song, os.path.join(basepath, 'score_content/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id)), c_artist_name)

                    #if os.path.exists(os.path.join(basepath, 'score_content/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id))):
                    #    img_n_byte_size = os.path.getsize(os.path.join(basepath, 'score_content/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id)))
                    #else:
                    #    img_n_byte_size = None

                        if os.path.exists(os.path.join(basepath, 'DB_FILE/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id))):
                            yp_n_byte_size = os.path.getsize(os.path.join(basepath, 'DB_FILE/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id)))
                        else:
                            yp_n_byte_size = None

                        #img_c_local_path = 'score_content/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id)
                        yp_c_local_path = c_score_id
                        #img_c_image_url = yuepu.group(1)
                        yp_c_image_url = self.getyuepu(song['URL'])
                        #img_c_extension = '.gif'
                        yp_c_extension = 'gp5'

                        #imgtsa = TRawScoreAsset(c_score_id=c_score_id, c_name=c_name, c_image_url=img_c_image_url,
                        #                        c_local_path=img_c_local_path, c_extension=img_c_extension,
                        #                        n_byte_size=img_n_byte_size)
                        #imgtsa.save(using='rds')

                        yptsa = TRawScoreAsset(c_id=c_score_id,c_score_id=c_score_id, c_name=c_name, c_image_url=yp_c_image_url,
                                               c_local_path=yp_c_local_path, c_extension=yp_c_extension,
                                               n_byte_size=yp_n_byte_size)

                        yptsa.save(using='rds')
                        print 'asset over'
                        #get liuyan
                        content = soup.find('ul', 'liuyanList_0421')
                        pattern = re.compile(
                            '<div.*?text">.*?<a.*?>(.*?)</a>.*?<p.*?msg_1125 title_color">(.*?)</p>.*?<p.*?time brief_color">(.*?)</p>',
                            re.S)
                        liuyan = re.findall(pattern, str(content))
                        if liuyan:

                            for item in liuyan:
                                c_score_comments_id = uuid.uuid4().hex
                                c_score_id = c_score_id
                                c_comments = item[1]
                                c_username = item[0]
                                d_evaluated = item[2].split(' ')[-1]
                                d_added = datetime.now()

                                trsc = TRawScoreComments(c_score_comments_id=c_score_comments_id, c_score_id=c_score_id,
                                                         c_comments=c_comments, c_username=c_username, d_evaluated=d_evaluated,
                                                         d_added=d_added)

                                trsc.save(using='rds')
                        print song['song_name'].encode('utf-8'), 'Download ok'
                    else:
                        print '{0} have no gtp'.format(song['song_name'])
                        pass
            else:
                failedlist.append(song)
        except Exception as e:
            print e.message

    def getyuepu(self, jtp_url):
        jsonstr = self.get(jtp_url)
        if jsonstr:
            try:
                jsonobj = json.loads(jsonstr)
                yuepuurl = jsonobj['data']['url']
                return yuepuurl
            except:
                return ''

    def mvgtpfiles(self, song, savename, singer_name):
        filename = os.path.join('/home/daohaoisbibi/tanqinba/gtp/', singer_name,
                                '{0}-{1}'.format(song['song_id'], song['song_name']), 'data.gp5')
        #print filename
        if os.path.exists(filename):
            os.rename(filename, savename)
            return True
        else:
            #print 'have no gtp!'
            return False

tqb = tanqinba()
'''
查询上一次终止时 爬取的song——id
注意：此处会生成一个txt文件于根目录
'''
markid = ''
if os.path.exists(os.path.join(basepath, '/home/daohaoisbibi/tanqinba/flag.txt')):
    with open('/home/daohaoisbibi/tanqinba/flag.txt', 'r') as m:
        markid = m.readline()

with open('/home/daohaoisbibi/tanqinba/tqbinfos.json', 'rb') as f:
    info = json.load(f)

    if markid:
        forflag = False
        for item in info:
            for song in item['Songs']:
                if markid == song['song_id']:
                    forflag = True
                if forflag:
                    # mark!
                    with open('/home/daohaoisbibi/tanqinba/flag.txt', 'w') as m:
                        m.write(song['song_id'])
                    tqb.getInfo(song)
    else:
        for item in info:
            for song in item['Songs']:
                # mark!
                with open('/home/daohaoisbibi/tanqinba/flag.txt', 'w') as m:
                    m.write(song['song_id'])
                tqb.getInfo(song)

with open('/home/daohaoisbibi/tanqinba/failed.json', 'w') as e:
    json.dump(failedlist, e)

print 'Download Over!'