# encoding: utf-8
from __future__ import unicode_literals
import json,sys,re,os.path
from api.models import *
from system.models import *
from datetime import datetime


with open('/home/jixin/havelist.json','r') as f:
    jsonobj = json.load(f)
    for item in jsonobj:
        try:
            artist_name = item.get('artist')
            ablumlist = item.get('ablumlist')
            artist_coverpic_id = item.get('artistpic')
            print artist_name
            #try:
            artist = Artist.objects.get(name__iexact=artist_name)
            artistassetphy = AssetPhysical()
            artistassetphy.id = artist_coverpic_id
            artistassetphy.local_path = 'pic_content/{0}/{1}/{2}'.format(artist_coverpic_id[0],artist_coverpic_id[1],artist_coverpic_id)
            artistassetphy.extension = 'png'
            artistassetphy.date_added = datetime.now()
            artistassetphy.save()
            artistasset = Asset()
            artistasset.id = artist_coverpic_id
            artistasset.name = artist.name
            artistasset.business_id = artist.id
            artistasset.business_type = 'artist.cover'
            artistasset.extension = 'png'
            artistasset.date_added = datetime.now()
            artistasset.physical_asset = artistassetphy
            artistasset.save()

            artist.cover_pic = artistasset
            artist.save()

            if len(ablumlist) > 0:
                for ablum in ablumlist:
                    print ablum.get('ablum')
                    try:
                        release = Release.objects.get(artist=artist,name__iexact=ablum.get('ablum'),cover_pic__isnull=True)
                        releaseassetphy = AssetPhysical()
                        releaseassetphy.id = ablum.get('ablumpic')
                        releaseassetphy.local_path = 'pic_content/{0}/{1}/{2}'.format(ablum.get('ablumpic')[0],ablum.get('ablumpic')[1],ablum.get('ablumpic'))
                        releaseassetphy.extension = 'png'
                        releaseassetphy.date_added = datetime.now()
                        releaseassetphy.save()
                        releaseasset = Asset()
                        releaseasset.id = ablum.get('ablumpic')
                        releaseasset.name = release.name
                        releaseasset.business_id = release.id
                        releaseasset.business_type = 'release.cover'
                        releaseasset.extension = 'png'
                        releaseasset.date_added = datetime.now()
                        releaseasset.physical_asset = releaseassetphy
                        releaseasset.save()

                        release.cover_pic = releaseasset
                        release.save()
                    except:
                        pass
        except Exception,e:
            print e