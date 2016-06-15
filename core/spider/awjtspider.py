# coding=utf-8
from __future__ import unicode_literals
import json
import sys,os.path,urllib2,cookielib,socket,zlib
from rds.models import *
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
    '''
    __req.add_headers = [
        ('Accept', 'application/javascript, */*;q=0.8'),
        ('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)')
    ]
    '''

    urllib2.install_opener(__req)

    def get(self, url, headers,retries=3):
        try:
            req = urllib2.Request(url,headers=headers)
            response = urllib2.urlopen(req, timeout=120)
            html = response.read()
            gzipped = response.headers.get('Content-Encoding')
            if gzipped:
                html = zlib.decompress(html, 16+zlib.MAX_WBITS)
            return html
        except Exception,what:
            print what
            if retries>0:
                return self.get(url,headers,retries-1)
            else:
                print "Get Failed",url
                return ' '

    def post(self, url, data, headers):
        try:
            req = urllib2.Request(url,data=data,headers=headers)
            return urllib2.urlopen(req, timeout=120).read()
        except urllib2.HTTPError, e:
            return e.read()
        except socket.timeout, e:
            return ''
        except socket.error, e:
            return ''

    def download(self, url, file):
        try:
            print file
            output = open(file, 'wb')
            output.write(urllib2.urlopen(url).read())
            output.close()
            #return os.path.getsize(file)
            print 'ok'
        except Exception as e:
            print e

    def get_cookies(self, key):
        for c in self.__cookie:
            if c.name == key:
                return c.value
        return ''

    def set_cookie(self, key, val, domain):
        ck = cookielib.Cookie(version=0, name=key, value=val, port=None, port_specified=False, domain=domain, domain_specified=False,  domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
        self.__cookie.set_cookie(ck)


class AiWan(HttpClient):
    def __init__(self):
        self.token = ""
        self.uid = ""
        self.label = {'556c30c0421aa978015f5df7': '华语', '556c30c0421aa978015f5df8': '日韩',
                      '556c30c0421aa978015f5df9': '欧美', '556c30c0421aa978015f5dfa': '民谣',
                      '556c30c0421aa978015f5dfb': '摇滚', '556c30c0421aa978015f5dfc': '流行'}
        self.type = {'556c30c0421aa978015f5ded': '简单', '556c30c0421aa978015f5dee': '中等',
                     '556c30c0421aa978015f5def': '困难'}

    def login_in(self):
        login_url = 'http://dynamic.iguitar.me/v1/login'
        login_headers = {
        'bundle-id': 'com.buluobang.iguitar',
        'device-id': '99000628615592',
        'device-model':' MI 4LTE',
        'device-os':'4.4.4',
        'lang': 'zh',
        'locale': 'CN',
        'platform': '1',
        'token': 'iguitar:eGxx9MZlrpmuEN2MEimlydNXCiNRxq2N0',
        'uid': '0',
        'version': '1.3.2',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '50',
        'Host': 'dynamic.iguitar.me',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/2.3.0',
        }
        login_data = 'tel=15321932892&zone=86&password=amkxMDA5MDk%3D%0A'
        login_result = self.post(login_url,login_data,login_headers)
        if login_result:
            try:
                decode_json = json.loads(login_result)
                if decode_json.get('result', 'not found') == 1:
                    print 'Login In Right'
                    self.uid = decode_json['data']['uid']
                    self.token = decode_json['data']['token']
                    return True
            except:
                print "False"
                return False
        print "False"
        return False

    def get_song_info(self, song_id):
        select_url = 'http://dynamic.iguitar.me/v1/score/{0}'.format(song_id)
        select_headers = {
        'bundle-id': 'com.buluobang.iguitar',
        'device-id': '99000628615592',
        'device-model':' MI 4LTE',
        'device-os':'4.4.4',
        'lang': 'zh',
        'locale': 'CN',
        'platform': '1',
        'token': self.token,
        'uid': str(self.uid),
        'version': '1.3.2',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '32',
        'Host': 'dynamic.iguitar.me',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/2.3.0',
        }
        select_data = 'scoreId={0}'.format(song_id)
        select_result = self.post(select_url, select_data, select_headers)
        if select_result:
            try:
                decode_json = json.loads(select_result)
                if decode_json['data']:
                    score_info = decode_json['data']['score']
                    c_score_id = uuid.uuid4().hex
                    c_artist_name = score_info.get('singer',None)
                    c_name = score_info.get('name',None)
                    c_desc = score_info.get('desc',None)
                    n_difficulty = score_info.get('diff',None)
                    c_src_from = "IGuitar"
                    d_added = datetime.now()
                    d_modified = datetime.now()
                    ts = TRawScore(c_score_id=c_score_id,c_artist_name=c_artist_name,c_name=c_name,
                                   c_desc=c_desc,n_difficulty=n_difficulty,c_src_from=c_src_from,
                                   d_added=d_added,d_modified=d_modified)
                    ts.save(using='rds')

                    savepath = os.path.join(basepath,'DB_FILE/{0}/{1}/'.format(c_score_id[0],c_score_id[1]))
                    if not os.path.exists(savepath):
                        print savepath
                        os.makedirs(savepath)
                    #self.download(score_info['thumb'],os.path.join(basepath,'score_content/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id)))
                    self.download(score_info['bgtsrc'],os.path.join(basepath,'DB_FILE/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id)))
                    #img_n_byte_size = os.path.getsize(os.path.join(basepath,'score_content/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id)))
                    yp_n_byte_size = os.path.getsize(os.path.join(basepath,'DB_FILE/{0}/{1}/{2}'.format(c_score_id[0],c_score_id[1],c_score_id)))
                    print yp_n_byte_size
                    #img_c_local_path = c_score_id
                    yp_c_local_path = c_score_id
                    #img_c_name = c_name
                    yp_c_name = c_name
                    #img_c_image_url = score_info['thumb']
                    yp_c_image_url = score_info['bgtsrc']
                    #img_c_extension = 'jpg'
                    yp_c_extension = 'unknow'
                    d_download = datetime.now()
                    #imgtsa = TRawScoreAsset(id=c_score_id,c_score_id=c_score_id,c_name=img_c_name,c_image_url=img_c_image_url,
                    #                     c_local_path=img_c_local_path,c_extension=img_c_extension,d_download=d_download,
                    #                     n_byte_size=img_n_byte_size)
                    #imgtsa.save(using='rds')

                    yptsa = TRawScoreAsset(c_id=c_score_id,c_score_id=c_score_id,c_name=yp_c_name,c_image_url=yp_c_image_url,
                                           c_local_path=yp_c_local_path,c_extension=yp_c_extension,d_download=d_download,n_byte_size=yp_n_byte_size)

                    yptsa.save(using='rds')
                    print '{0} saved!'.format(c_name)
            except Exception as e:
                print e.message


g = AiWan()
#get mark!
markid = ''
if os.path.exists('/home/daohaoisbibi/aitanjita/awjtflag.txt'):
    with open('/home/daohaoisbibi/aitanjita/awjtflag.txt','r') as m:
        markid = m.readline()

if g.login_in():
    #注意：路径
    with open('/home/daohaoisbibi/aitanjita/awjtinfos.json','rb') as f:
        info = json.load(f)
        if markid:
            forflag = False
            for item in info:
                if markid == item['scoreId']:
                    forflag = True
                else:
                    pass
                if forflag:
                    #mark!
                    with open('/home/daohaoisbibi/aitanjita/awjtflag.txt','w') as m:
                        m.write(item['scoreId'])

                    g.get_song_info(item['scoreId'])

        else:
            for item in info:
                #mark!
                with open('/home/daohaoisbibi/aitanjita/awjtflag.txt','w') as m:
                    m.write(item['scoreId'])

                g.get_song_info(item['scoreId'])

    print "DownLoad Over!!!!"

#label2 type 难度
#简单：label2=556c30c0421aa978015f5ded
#中等：label2=556c30c0421aa978015f5dee
#困难：label2=556c30c0421aa978015f5def


#label4 分类 label
#华语：556c30c0421aa978015f5df7
#欧美：556c30c0421aa978015f5df9
#日韩：556c30c0421aa978015f5df8
#流行：556c30c0421aa978015f5dfc
#民谣：556c30c0421aa978015f5dfa
#摇滚：556c30c0421aa978015f5dfb