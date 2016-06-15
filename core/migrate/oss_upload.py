# encoding: utf-8
from __future__ import print_function

import os
import sys
import os.path

import oss2
from django.utils import timezone

from system.models import AssetPhysical


def upload_dir(path):
    # path = "E:/yzkj/youpua-server/uploads/pic_content/0/2//02e5bbe739ab4de1ae5237fafd45e7a7.jpg"
    path = u"E:\\yzkj\\youpua-server\\uploads\\pic_content"
    for parent, dirnames, filenames in os.walk(path):
    # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for dirname in dirnames:  # 输出文件夹信息
            pass

        for filename in filenames:  # 输出文件信息
            local_file_path = os.path.join(parent, filename)
            remote_file_path = os.path.join(parent, filename).replace(path + '\\', '').replace('\\', '/')
            file_id = filename.split('.')[0]
            print(file_id)
            db_count = AssetPhysical.objects.filter(id__exact=file_id).filter(oss_object__isnull=False).count()
            print(db_count)
            is_in_db = db_count > 0
            if not is_in_db:
                upload_to_oss(local_file_path, remote_file_path)
                asset = AssetPhysical.objects.filter(id__exact=file_id)[0]
                asset.oss_object = remote_file_path
                asset.update_time = timezone.localtime(timezone.now())
                asset.save()


def upload_to_oss(local_file_path, remote_file_path):
    with open(local_file_path, 'rb') as b:
        # upload to aliyun oss
        auth = oss2.Auth('FJykuToJhsRYZOZ0', 'kWZ9rWp7HmIM90j4GrQNZU3QLjVUDn')
        try:
            service = oss2.Bucket(auth, 'http://' + 'oss-cn-beijing' + '.aliyuncs.com', 'letz-image1')
            service.put_object(remote_file_path, b, progress_callback=percentage)

        except Exception as e:
            print(e)


def percentage(consumed_bytes, total_bytes):
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        print('\r{0}% '.format(rate), end='')

        sys.stdout.flush()


upload_dir()