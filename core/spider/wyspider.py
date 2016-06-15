# coding=utf-8
from __future__ import unicode_literals
import json,re
import sys,os.path,urllib2,cookielib,socket,zlib
from bs4 import BeautifulSoup
import uuid


reload(sys)
sys.setdefaultencoding('utf-8')


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
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
        ('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0'),
        ('Host', 'music.163.com'),
        ('Accept-Language', 'en-US,en;q=0.5'),
        ('Accept-Encoding', 'gzip, deflate'),
        ('Connection', 'keep-alive'),
        ('Cookie','usertrack=ZUcIhlcUM8SmTEqkKRUZAg==; Province=010; City=010; _ntes_nnid=f41e535517bbc1ff8d7d1e36a7bd5676,1460941765441; _ntes_nuid=f41e535517bbc1ff8d7d1e36a7bd5676; _ga=GA1.2.523686512.1460941766; JSESSIONID-WYYY=689bae0117a527091838dfb1dd012e8ef517ecb0c04d033ff71612f8034b1db989df57cf1016bc820b49bc4f0a878aba643ba85f75e5f06c384ec478ab4a07fac4c3bc02c310c332f2dcfcac53ad3e3306d20e6029c8183229b06b9f688873bc33b166e0c705db26971cb085a3268460f62a77fd19ce17629ca19838e40a9f4239561b2d%3A1461065150172; _iuqxldmzr_=25; visited=true; __utma=94650624.523686512.1460941766.1461054702.1461063152.6; __utmz=94650624.1461032015.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmc=94650624; __utmb=94650624.6.10.1461063152')

    ]

    urllib2.install_opener(__req)

    def get(self, url,refer=None,retries=3):
        try:
            req = urllib2.Request(url)
            if not (refer is None):
                req.add_header('Referer', refer)
            response = urllib2.urlopen(req, timeout=120)
            html = response.read()
            gzipped = response.headers.get('Content-Encoding')
            if gzipped:
                html = zlib.decompress(html, 16+zlib.MAX_WBITS)
            return html
        except Exception,what:
            print what
            if retries>0:
                return self.get(url,retries-1)
            else:
                print "Get Failed",url
                return ' '

    def post(self, url, data,refer=None):
        try:
            req = urllib2.Request(url,data=data)
            if not (refer is None):
                req.add_header('Referer', refer)
            return urllib2.urlopen(req, timeout=120).read()
        except urllib2.HTTPError, e:
            return e.read()
        except socket.timeout, e:
            return ''
        except socket.error, e:
            return ''

    def download(self, url, savepath, file):
        try:
            if not os.path.exists(savepath):
                os.makedirs(savepath)
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
        ck = cookielib.Cookie(version=0, name=key, value=val, port=None, port_specified=False, domain=domain, domain_specified=False,  domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
        self.__cookie.set_cookie(ck)


class WangYi(HttpClient):
    def __init__(self):
        self.song_category = {
            '1001': '华语/男',
            '1002': '华语/女',
            '1003': '华语/组合',
            '2001': '欧美/男',
            '2002': '欧美/女',
            '2003': '欧美/组合',
            '3001': '日韩/男',
            '3002': '日韩/女',
            '3003': '日韩/组合',
            '4001': '其他/男',
            '4002': '其他/女',
            '4003': '其他/组合'
        }

        self.singer_category = [str(x) for x in range(65,91)]
        self.singer_category.append(str(0))
        self.singer_id_list = []

    #获取所有歌手的信息
    def get_all_singer(self):
        for songitem in self.song_category.keys():
            for singeritem in self.singer_category:
                url = 'http://music.163.com/discover/artist/cat?id={0}&initial={1}'.format(songitem,singeritem)
                pagecode = self.get(url,refer='http://music.163.com')
                soup = BeautifulSoup(pagecode)
                content = soup.findAll(attrs={'class':'nm nm-icn f-thide s-fc0'})
                for item in content:
                    pattern = re.compile('<a.*? href=".*?id=(.*?)" .*?>(.*?)</a>', re.S)
                    m = re.search(pattern, str(item))
                    self.singer_id_list.append({'singer': m.group(2), 'singerid':  m.group(1), 'singer_category': songitem})
                #print '{0},{1} get over'.format(songitem,singeritem)

        with open('/home/jixin/singerlist.json','wb') as f:
            json.dump(self.singer_id_list,f)

        print "Get All!!!"

    #获取所有歌手的专辑信息 并存储该歌手所有专辑的图片
    def get_album_list(self):
        singer_album_list = []
        #读取mark记录 获取上次执行脚本截止的singerid
        #markid = ''
        #if os.path.exists('/home/daohaoisbibi/WYPIC//flag.txt'):
        #    with open('/home/daohaoisbibi/WYPIC//flag.txt','r') as m:
        #        markid = m.readline()
        #forflag = True
        with open('/home/jixin/minyao.json','rb') as f:
            decodejson = json.load(f)
            #if markid:
             #   forflag = False
            for item in decodejson:
             #   if not forflag:
             #       if item.get('singerid') == markid:
             #           forflag = True
            #    else:
                singer = item.get('singer')
                singerid = item.get('singerid')
                ablum_list = []
                url = 'http://music.163.com/artist/album?id={0}&limit=200'.format(item.get('singerid','None'))
                pagecode = self.get(url,refer='http://music.163.com/')
                #print item.get('singerid')
                soup = BeautifulSoup(pagecode)
                #print soup
                #获取歌手的图片
                try:
                    #singer_img = soup.find('div',attrs={'class':'n-artist f-cb'}).img['src']
                    #singer_id = uuid.uuid4().hex
                    #savepath = os.path.join('/home/jixin/', 'WYPIC/{0}/{1}/'.format(singer_id[0],singer_id[1]))
                    #singer_img = soup.find('div',attrs={'class':'u-cover u-cover-alb3'}).img['src']
                    #self.download(str(singer_img)[0:-14], savepath, os.path.join(savepath,singer_id))
                    #获取歌手所有专辑的图片
                    content = soup.findAll(attrs={'class':'u-cover u-cover-alb3'})
                    for ablum in content:
                        try:
                            pattern = re.compile('<div.*?title="(.*?)">.*?[.\n]+.*?src="(.*?)".*?[.\n]+.*?href="\/album\?id=(.*?)">')
                            m = re.search(pattern,str(ablum))
                            ablumurl = 'http://music.163.com/album?id={0}'.format(m.group(3))

                            ablumpagecode = self.get(ablumurl,refer=ablumurl)
                            ablumsoup = BeautifulSoup(ablumpagecode)
                            ablumcontent = ablumsoup.find('ul',attrs={'class':'f-hide'})
                            abluminfo = ablumsoup.find_all('p',attrs={'class':'intr'})
                            ablumtime = ''
                            ablumcompany = ''
                            try:
                                ablumtime = re.search('</b>(.*?)</p>',str(abluminfo[1])).group(1)
                                ablumcompany = re.search('<b>.*?[.\n]+(.*?)[.\n]+.*?</p>',str(abluminfo[2])).group(1)
                            except:
                                pass
                            print ablumcompany
                            ablum_song_list = []

                            try:
                                pattern = re.compile('<a href=".*?id=(.*?)">(.*?)</a>',re.S)
                                songs = re.findall(pattern,str(ablumcontent))
                                for song in songs:
                                    songid = song[0]
                                    songname = song[1]
                                    songurl = 'http://music.163.com/song?id={0}'.format(songid)
                                    #songcode = self.get(songurl)
                                    #songsoup = BeautifulSoup(songcode)
                                    #songimg = songsoup.find('img',attrs={'class':'j-img'})['data-src']
                                    #self.download(songimg,os.path.join(dirpath,songname))
                                    ablum_song_list.append({'songid':songid,'songname':songname,})
                                    #print '{0}-{1} img over'.format(singer,songname)

                            except Exception,what:
                                print what,'11111'

                            #album_id = uuid.uuid4().hex
                            #ablumimg = os.path.join(dirpath,m.group(1))
                            #savepath = os.path.join('/home/daohaoisbibi/', 'WYPIC/{0}/{1}/'.format(album_id[0],album_id[1]))
                            #self.download(m.group(2)[0:-14],savepath,os.path.join(savepath,album_id))

                            ablum_list.append({'ablumname':m.group(1),'ablumid':m.group(3),'songlist':ablum_song_list,
                                               'ablumtime':ablumtime,'ablumcompany':ablumcompany})

                            #print '{0},{1} over'.format(singerid,m.group(1))
                        except Exception,what:
                                print what,'2222'
                    singer_album_list.append({'singer':singer, 'singerid':singerid, 'ablum':ablum_list})
                    #with open('/home/daohaoisbibi/WYPIC/flag.txt','w') as mark:
                    #    mark.write(singerid)
                except:
                    print 'error: 404'

            with open('/home/jixin/minyaosinger_ablum_list.json','wb') as f:
                json.dump(singer_album_list,f)

        print "Get All!!!"
    #获取专辑每首歌的信息 包括歌名 id 图片url（此图片与专辑图片一致可忽略）并生成json数据
    def get_ablum_songs(self):
        with open('/home/daohaoisbibi/WYPIC/singer_ablum_list.json','r') as f:
            decodejson = json.load(f)
            singers = []
            for item in decodejson:
                singer = item.get('singer')
                singerid = item.get('singerid')
                ablums = item.get('ablum')
                ablum_song_list = []
                ablums_list = []
                if ablums:
                    for ablum in ablums:
                        ablumname = ablum.get('ablumname')
                        ablumid = ablum.get('ablumid')
                        url = 'http://music.163.com/album?id={0}'.format(ablumid)
                        pagecode = self.get(url,refer=url)
                        #dirpath = os.path.join('/home/daohaoisbibi/WYPIC/',singer)
                        #if not os.path.exists(dirpath):
                        #    try:
                        #        os.mkdir(dirpath)
                        #    except:
                        #        pass
                        soup = BeautifulSoup(pagecode)
                        content = soup.find('ul',attrs={'class':'f-hide'})

                        try:
                            pattern = re.compile('<a href=".*?id=(.*?)">(.*?)</a>',re.S)
                            songs = re.findall(pattern,str(content))
                            for song in songs:
                                songid = song[0]
                                songname = song[1]
                                #songurl = 'http://music.163.com/song?id={0}'.format(songid)
                                #songcode = self.get(songurl)
                                #songsoup = BeautifulSoup(songcode)
                                #songimg = songsoup.find('img',attrs={'class':'j-img'})['data-src']
                                #self.download(songimg,os.path.join(dirpath,songname))
                                ablum_song_list.append({'songid':songid,'songname':songname})
                                print '{0}-{1}'.format(singer,songname)

                        except:
                            pass
                        ablums_list.append({'ablumid':ablumid,'ablumname':ablumname,'song_list':ablum_song_list})
                    singers.append({'singer':singer,'singerid':singerid,'ablums_list':ablums_list})
            with open('/home/daohaoisbibi/WYPIC/singers_ablums_all.json','wb') as f:
                json.dump(singers,f)


wy = WangYi()
#先获取所有歌手信息保存为json文件
#wy.get_all_singer()
#遍历上个方法生成的json文件，下载歌手图片及专辑图片，并将歌手及其所有专辑信息生成json文件
wy.get_all_singer()
#遍历上个方法生成的json文件，获取该歌手所有的歌曲及歌曲封面（注！！歌曲封面与其所在专辑封面相同，故可忽略此方法）
#wy.get_ablum_songs()