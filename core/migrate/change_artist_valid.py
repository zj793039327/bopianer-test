# coding=utf-8
from __future__ import unicode_literals
from api.models import *
from django.db.models import Q


artists = Artist.objects.filter(valid=1)
for artist in artists:
    recordings = Recording.objects.filter(artist=artist)
    scorecount = 0
    for i in recordings:
        #print artist.name,i.name
        score = Score.objects.filter(Q(recording=i), Q(asset_type=2), Q(status=10))
        for item in score:
            item.status = 10
        if score.count() == 0:
            i.valid = 2
            i.save()
        else:
            i.valid = 1
            i.save()
        scorecount += score.count()
    if scorecount == 0:
        artist.valid = 2
        artist.save()
        #print '{0} have no score'.format(artist.name)
    else:
        #print '{0} have {1} score'.format(artist.name,scorecount)
        pass