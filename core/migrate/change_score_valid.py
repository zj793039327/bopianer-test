# coding=utf-8
from __future__ import unicode_literals
from api.models import *
from django.db.models import Q
from system.models import *
from rds.models import *


raw_scores = TRawScore.objects.using('rds').filter(Q(c_src_from='17jita')|Q(c_src_from='91jita')|Q(c_src_from='wojita')|
                                      Q(c_src_from='mumujita')|Q(c_src_from='jitaba')|Q(c_src_from='jitashe')|
                                      Q(c_src_from='sooopu')|Q(c_src_from='yuesir'))
for item in raw_scores:
    try:
        score = Score.objects.get(id__iexact=item.c_score_id)
        asset = Asset.objects.filter(business_id=score.id)[0]
        if score.name.lower() not in asset.name.lower():
            print score.name,asset.name,"error"
            score.status = 30
            score.save()
        else:
            score.status = 10
            score.save()
            print score.name,asset.name,"right"
    except Exception,e:
        print e
