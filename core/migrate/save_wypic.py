# coding:utf-8
from __future__ import unicode_literals
import json,re
import sys,os.path,urllib2,cookielib,socket,zlib
from bs4 import BeautifulSoup
import uuid
import json
from api.models import *


havelist = []
with open('/home/jixin/singer_ablum_list.json','r') as f:
    jsonobj = json.load(f)
    artists = Artist.objects.filter(valid=1)
    for artist in artists:
        for item in jsonobj:
            artistname = item.get('singer')
            artistid = item.get('singer_name')
            ablum = item.get('ablum')
            try:
                #artists = Artist.objects.filter(valid=1)
                if artist.name == artistname or artist.name.replace('乐队','') == artistname:
                    ablumlist = []
                    for i in ablum:
                        ablumname = i.get('ablumname')
                        ablumid = i.get('album_name')
                        try:
                            release = Release.objects.filter(name__iexact=ablumname,artist=artist)
                            if release is not None:
                                for i in release:
                                    i.cover_pic_url = '{0}/{1}/{2}.jpg'.format(ablumid[0],ablumid[1],ablumid)
                                    print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
                                    i.save()
                        except Exception,what:
                            pass

                    try:
                        artist.cover_pic_url = '{0}/{1}/{2}.jpg'.format(artistid[0],artistid[1],artistid)
                        print artist.cover_pic_url
                        artist.save()
                    except Exception,e:
                        print e
                    print artistname
            except Exception,what:
                pass
