# encoding: utf-8
from __future__ import unicode_literals
import json,sys,re,os.path
from rds.models import *
from datetime import datetime
import glob,uuid
import shutil,zipfile
reload(sys)
sys.setdefaultencoding('utf-8')
basepath = '/home/jixin/Desktop/'
SCORE_KEY = (
    ('C调', '10'),
    ('G调', '50'),
    ('F调', '40'),
)
SCORE_PLAY_TYPE = (
    ('指弹', 1),
    ('弹唱', 2),
)
# 原版
# 简单版
#加载json数据
with open('/home/jixin/Desktop/Resource/yuesir/scorelists2.json','r') as f:
    jsonobj = json.load(f)
    for item in jsonobj:
        if item is not None:
            """
            score_key = None
            score_play_type = None
            is_tan = 2
            is_yuan = 2
            #print item.get('title')
            for i in SCORE_KEY:
                if i[0] in item.get('score_name'):
                    score_key = i[1]
                    break
            for i in SCORE_PLAY_TYPE:
                if i[0] in item.get('score_name'):
                    score_play_type = i[1]
                    break
            if '原版' in item.get('score_name'):
                is_yuan = 1
            if '简单' in item.get('score_name'):
                is_tan = 1
            if '简易' in item.get('score_name'):
                is_tan = 1
            score_name = item.get('score_name').strip()
            if '(' in score_name:
                score_name = score_name.split('(')[0]
            if '（' in score_name:
                score_name = score_name.split('（')[0]

            print score_name
            """
            extension = item.get('extension')
            #artist = item.get('artist').strip()
            #src_from = 'sooopu'
            #share_count = 0
            #if item.get('share_count'):
            #    share_count = int(item.get('share_count'))
            id = item.get('id')
            score_name = item.get('score_name')
           # d_added = datetime.now()
           # d_modified = datetime.now()

            #ts = TRawScore(c_score_id=id, c_artist_name=artist, c_name=score_name,is_original=is_yuan,is_simple=is_tan,n_key_play=score_key,
            #           n_asset_type_id=2,n_play_type_id=score_play_type,c_src_from=src_from,d_added=d_added,d_modified=d_modified,n_count_view=share_count)
            #ts.save(using='rds')
            """
            filepath = os.path.join(basepath,'Resource/yuesir/{0}'.format(id))
            flag = False
            for i in glob.glob('{0}/*'.format(filepath)):
                filename = os.path.join(filepath,i)
                asset_size = os.path.getsize(filename)
                if asset_size > 0:
                    print asset_size
                    flag = True
                    local_path = id
                    business_sort = int(i.split('/')[-1])
                    print business_sort
                    yptsa = TRawScoreAsset(c_score_id=id, c_name=score_name,
                                           c_local_path=local_path, c_extension=extension,c_tag='Chords',
                                           n_byte_size=asset_size,business_sort=business_sort)
                    yptsa.save(using='rds')
                    asset_id = yptsa.c_id
                    savepath = os.path.join(basepath,'DB_FILE/{0}/{1}/'.format(asset_id[0],asset_id[1]))
                    #print savepath
                    if not os.path.exists(savepath):
                        os.makedirs(savepath)
                    shutil.copy(filename,'{0}{1}'.format(savepath,asset_id))
                else:
                    flag = False
            #if flag:
                #ts.save(using='rds')
            """
            filepath = os.path.join(basepath,'Resource/yuesir/{0}.{1}'.format(id,extension))
            try:
                zpfd = zipfile.ZipFile(filepath,'r')
                for i in zpfd.namelist():
                    tmp = zpfd.read(i)
                    yptsa = TRawScoreAsset()
                    yptsa.c_score_id = id
                    yptsa.c_name = score_name
                    yptsa.c_local_path = id
                    asset_id = yptsa.c_id
                    savepath = os.path.join(basepath,'DB_FILE/{0}/{1}/'.format(asset_id[0],asset_id[1]))
                    #print savepath
                    if not os.path.exists(savepath):
                        os.makedirs(savepath)
                    with open('{0}{1}'.format(savepath,asset_id),'w') as f:
                        f.write(tmp)
                    asset_size = os.path.getsize('{0}{1}'.format(savepath,asset_id))
                    business_sort = int(i.split('.')[0])
                    extension = i.split('.')[-1]

                    yptsa.c_extension = extension
                    yptsa.c_tag = 'Chords'
                    yptsa.n_byte_size = asset_size
                    yptsa.business_sort = business_sort
                    print business_sort
                    yptsa.save(using='rds')
                zpfd.close()
            except:
                pass

