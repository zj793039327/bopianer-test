# encoding: utf-8

__author__ = 'zjhome'
import logging
# from Queue import Queue
from threading import Thread
from multiprocessing import Process,Lock,Queue
from rds.models import *
from api.models import *
from system.models import *
from youpua_server.settings import MUSIC_BRAINZ
from core.code.normalcode import NormalCode
from core.business_error import BusinessError
from core.utils import string_utils
from core.utils.music_brainz import MusicBrainZ
from time import sleep

if __name__ == '__builtin__':
    logger = logging.getLogger('core.migrate.rds_to_ypa')
else:
    logger = logging.getLogger(__name__)


def _get_artist(json_rec):
    json_artist = json_rec['artist-credit'][0]
    artist_id = json_artist['artist']['id']
    artist_count = Artist.objects.filter(mbid__iexact=artist_id).count()
    if artist_count == 0:
        # 没有有artist
        art = MusicBrainZ.get_mb_artist(artist_id, MUSIC_BRAINZ.get('req_timeout'))
        art.save()
    else:
        art = Artist.objects.filter(mbid__iexact=artist_id)[0]
    return art


def _save_release_cover(cover_pic_url, rel):
    ap_count = AssetPhysical.objects.filter(remote_url__iexact=cover_pic_url).count()
    if ap_count == 0:

        ap = AssetPhysical()
        ap.remote_url = cover_pic_url
        ap.date_download = None
        ap.extension = string_utils.get_suffix(cover_pic_url.strip())
        ap.local_path = None
        ap.save()
    else:
        ap = AssetPhysical.objects.filter(remote_url__iexact=cover_pic_url)[0]

    a2Rel = Asset()
    a2Rel.physical_asset = ap
    a2Rel.extension = ap.extension
    a2Rel.business_id = rel.id
    a2Rel.business_type = NormalCode.ASSET_BUSINESS_RELEASE_COVER_PIC
    a2Rel.name = string_utils.get_file_name_from_url(cover_pic_url)
    a2Rel.save()

    return a2Rel


def _get_release(art, json_rec):
    if not json_rec.get('releases'):
        logger.debug('with out releases')
        return None

    json_release = json_rec['releases']
    real_release = {}
    release_id = ''

    # choose first release with cover
    has_cover_art = False
    for release in json_release:
        _id = release['id']
        data = MusicBrainZ.get_release_cover_art(_id, MUSIC_BRAINZ.get('req_timeout'))
        if data == 'next_release':
            continue
        else:
            release_id = _id
            real_release = release
            cover_pic_url = data
            has_cover_art = True
            break

    if not has_cover_art:
        release_id = json_release[0]['id']
        real_release = json_release[0]
        cover_pic_url = None
    release_count = Release.objects.filter(mbid__iexact=release_id).count()

    if release_count == 0:
        # 没有有artist
        rel = Release()
        rel.mbid = release_id
        rel.name = real_release.get('title')
        rel.artist = art
        rel.save()
    else:
        rel = Release.objects.filter(mbid__iexact=release_id)[0]

    if has_cover_art:
        asset = _save_release_cover(cover_pic_url, rel)
        rel.cover_pic_id = asset.id
        rel.save()

    return rel


def _get_record(art, json_rec, rel):
    rec_id = json_rec['id']
    rec = Recording()
    rec.mbid_recording = rec_id
    rec.name = json_rec.get('title')
    rec.release = rel
    rec.artist = art
    rec.save()
    return rec


def save_music_repo(score):
    data = MusicBrainZ.search_mb_recording(score.c_artist_name, string_utils.trim_version(score.c_name))
    json_rec = data['recordings'][0]
    rec_id = json_rec['id']
    rec_count = Recording.objects.filter(mbid_recording__iexact=rec_id).count()
    if rec_count > 0:
        rec = Recording.objects.filter(mbid_recording__iexact=rec_id)[0]
        return rec
    else:
        art = _get_artist(json_rec)
        rel = _get_release(art, json_rec)
        rec = _get_record(art, json_rec, rel)
    rec.score = json_rec.get('score')
    return rec


def save_score(raw, recording):
    # 1 save main table
    cooked = Score()
    # pk is the same
    cooked.id = raw.c_score_id

    cooked.recording_score = recording.score
    cooked.recording = recording
    cooked.name = recording.name

    version_num = Score.objects.filter(recording__id__iexact=recording.id).count()
    cooked.version = version_num + 1
    cooked.id = raw.c_score_id
    cooked.rating = raw.c_rating
    cooked.count_rating = raw.n_count_rating
    cooked.count_view = raw.n_count_view
    cooked.count_review = raw.n_count_review
    cooked.count_view_week = raw.n_count_view_week
    # set cover_pic_id
    cooked.save()

    # 2 save assets
    # 2.1 cover_pic
    if recording.release and recording.release.cover_pic_id:
        # part1
        cooked.cover_pic_id = recording.release.cover_pic_id
        cooked.save()
        # part2
        asset_cover = Asset()
        asset_cover.name = recording.release.cover_pic.name
        asset_cover.physical_asset = recording.release.cover_pic.physical_asset
        asset_cover.extension = recording.release.cover_pic.extension
        asset_cover.business_type = NormalCode.ASSET_BUSINESS_SCORE_COVER_PIC
        asset_cover.business_id = cooked.id
        asset_cover.save()
    # 2.2 data asset

    raw_assets = TRawScoreAsset.objects.using('rds').filter(c_score_id__iexact=raw.c_score_id)
    score_file_path_pattern = 'score_content/{0}/{1}/{2}'

    for asset in raw_assets:
        cooked.score_type = asset.c_tag

        cooked.asset_type = NormalCode.get_score_asset_type(asset.c_extension)
        cooked.instruments_type = NormalCode.guess_instruments_type(asset.c_tag)
        cooked.save()

        asset_data = AssetPhysical()
        asset_data.remote_url = asset.c_image_url
        asset_data.extension = asset.c_extension

        path_raw = asset.c_local_path
        asset_data.local_path = score_file_path_pattern.format(path_raw[0], path_raw[1], path_raw)
        asset_data.id = asset.c_id
        asset_data.byte_size = asset.n_byte_size

        asset_data.date_download = asset.d_download
        asset_data.tag = asset.c_tag
        asset_data.save()

        asset_logical = Asset()
        asset_logical.physical_asset = asset_data
        asset_logical.name = asset.c_name + '.' + asset.c_extension
        asset_logical.business_id = raw.c_score_id
        asset_logical.business_type = NormalCode.ASSET_BUSINESS_SCORE_FILE
        asset_logical.save()


def migrate_score(counter, raw):
    try:
        counter -= 1
        logger.debug(str(counter) + ' left ' + raw.c_score_id)
        recording = save_music_repo(raw)
        save_score(raw, recording)
        if raw.c_src_from is None:
            raw.c_src_from = 'ug'
        raw.is_fetch_detail = 1
        raw.save()
    except BusinessError as e:
        logger.error(e)
        logger.debug('%d was error, id: %s ', counter, raw.c_score_id)
        raw.is_fetch_detail = 2
        raw.save()


def main():
    # scores = TRawScore.objects.using('rds').filter(is_fetch_detail__iexact=None).order_by('c_name')
    #count = TRawScore.objects.using('rds').raw('''select s.* from t_raw_score as s,t_raw_score_asset as a where s.is_fetch_detail is NULL and s.c_score_id=a.c_score_id ORDER BY s.c_name''').count()
    #logger.debug('begin migrate rds score data, there are ' + str(count) + ' records')
    while 1:
    #counter = len(scores)
        if q.empty():
            print '------------------------------------'
            #scores = TRawScore.objects.using('rds').filter(is_fetch_detail__iexact=None).order_by('-c_name')[0:5000]
            scores = TRawScore.objects.using('rds').raw('''select s.* from t_raw_score as s,t_raw_score_asset as a where s.is_fetch_detail is NULL and s.c_score_id=a.c_score_id ORDER BY s.c_name limit 5000''')
            logger.debug('begin migrate rds score data, there are ' + str(len(list(scores))) + ' records')
            for raw in scores:
                q.put(raw)
            if len(list(scores)) < 5000:
                break


####################
# build to a async task
def worker(q):
    while True:
        raw = q.get()
        counter = q.qsize()
        migrate_score(counter, raw)
        #q.task_done()

# lock = Lock()
q = Queue(5000)
for i in range(MUSIC_BRAINZ.get('req_thread_count')):
    t = Process(target=worker,args=(q,))
    t.daemon = True
    t.start()

main()

#q.join()  # block until all tasks are done
# print get_mb_artist('d5cc67b8-1cc4-453b-96e8-44487acdebea')
# print get_release_cover_art('44f67ad5-cdff-3036-80e9-bee67402ded01')
# get_release_cover_art('76df3287-6cda-33eb-8e9a-044b5e15ffdd')


