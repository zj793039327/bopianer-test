# encoding: utf-8
from __future__ import unicode_literals
from core.chconverter.langconv import *
from api.models import *


artists = Artist.objects.all().order_by('-name')
"""
for artist in artists:
    artist.name = Converter('zh-hans').convert(artist.name)
    artist.alias = Converter('zh-hans').convert(artist.alias)
    artist.save()
    print artist.name
print 'over'
"""
releases = Release.objects.all().order_by('-name')
for release in releases:
    release.name = Converter('zh-hans').convert(release.name)
    release.save()
    print release.name
"""
recordings = Recording.objects.all().order_by('-name')[0:100000]
for recording in recordings:
    recording.name = Converter('zh-hans').convert(recording.name)
    recording.save()
    print recording.name

scores = Score.objects.all().order_by('-name')[0:100000]
for score in scores:
    score.name = Converter('zh-hans').convert(score.name)
    score.save()
    print score.name
"""