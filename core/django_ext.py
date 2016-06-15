# encoding: utf-8
from __future__ import absolute_import

import os
import datetime
import posixpath
from urlparse import urljoin

import six
from django.core.files import File
from django.utils.encoding import force_text, filepath_to_uri, force_bytes
from oss2 import Auth, Service, BucketIterator, Bucket, ObjectIterator
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.files.storage import Storage
from oss2.api import _normalize_endpoint
import bopianer.settings

from django.utils.deconstruct import deconstructible
import uuid


# django 的一些扩展


class AliyunOperationError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BucketOperationMixin(object):
    def _get_bucket(self, auth):
        return Bucket(auth, self.end_point, self.bucket_name)

    def _list_bucket(self, service):
        return [bucket.name for bucket in BucketIterator(service)]

    def _create_bucket(self, auth):
        bucket = self._get_bucket(auth)
        bucket.create_bucket(settings.BUCKET_ACL_TYPE)
        return bucket

    def _check_bucket_acl(self, bucket):
        if bucket.get_bucket_acl().acl != settings.BUCKET_ACL_TYPE:
            bucket.put_bucket_acl(settings.BUCKET_ACL_TYPE)
        return bucket


class AliyunBaseStorage(Storage):
    """
    Aliyun OSS2 Storage
    """
    location = ""
    acl = ""
    bucket_name = ""

    def __init__(self):
        self.access_key_id = self._get_config('ACCESS_KEY_ID')
        self.access_key_secret = self._get_config('ACCESS_KEY_SECRET')
        self.end_point = _normalize_endpoint(self._get_config('END_POINT').strip())

        self.auth = Auth(self.access_key_id, self.access_key_secret)
        self.service = Service(self.auth, self.end_point)

        # if self.bucket_name not in self._list_bucket(self.service):
        # # create bucket if not exists
        # self.bucket = self._create_bucket(self.auth)
        # else:
        # # change bucket acl if not consists
        # self.bucket = self._check_bucket_acl(self._get_bucket(self.auth))
        # make sure the bucket must be there
        self.bucket = Bucket(self.auth, self.end_point, self.bucket_name)

    def _get_config(self, name):
        """
        Get configuration variable from environment variable
        or django setting.py
        """
        config = os.environ.get(name, getattr(settings, name, None))
        if config is not None:
            if isinstance(config, six.string_types):
                return config.strip()
            else:
                return config
        else:
            raise ImproperlyConfigured(
                "Can't find config for '%s' either in environment"
                "variable or in setting.py" % name)

    def _clean_name(self, name):
        """
        Cleans the name so that Windows style paths work
        """
        # Normalize Windows style paths
        clean_name = posixpath.normpath(name).replace('\\', '/')

        # os.path.normpath() can strip trailing slashes so we implement
        # a workaround here.
        if name.endswith('/') and not clean_name.endswith('/'):
            # Add a trailing slash as it was stripped.
            return clean_name + '/'
        else:
            return clean_name

    def _normalize_name(self, name):
        """
        Normalizes the name so that paths like /path/to/ignored/../foo.txt
        work. We check to make sure that the path pointed to is not outside
        the directory specified by the LOCATION setting.
        """

        base_path = force_text(self.location)
        base_path = base_path.rstrip('/')

        final_path = urljoin(base_path.rstrip('/') + "/", name)

        base_path_len = len(base_path)
        if (not final_path.startswith(base_path) or
                    final_path[base_path_len:base_path_len + 1] not in ('', '/')):
            raise SuspiciousOperation("Attempted access to '%s' denied." %
                                      name)
        return final_path.lstrip('/')

    def _get_target_name(self, name):
        name = self._normalize_name(self._clean_name(name))

        if self.acl == 'private':
            name = name.split('/')[-1]
            name = 'encoded/{0}/{1}/{2}_en'.format(name[0],name[1],name)
        elif self.acl == 'public-read':
            if len(name) < 32:
                name = uuid.uuid4().hex
            name = '{0}/{1}/{2}.jpg'.format(name[0],name[1],name)
        else:
            pass
        if six.PY2:
            name = name.encode('utf-8')
        return name

    def _open(self, name, mode='wrb'):
        name = self._get_target_name(name)
        return AliyunFile(name, self, mode)

    def _save(self, name, content):
        name = self._get_target_name(name)
        content.open()
        content_str = b''.join(chunk for chunk in content.chunks())
        self.bucket.put_object(name, content_str)
        content.close()

        return self._clean_name(name)


    def get_file_header(self, name):
        name = self._get_target_name(name)
        return self.bucket.head_object(name)

    def exists(self, name):
        return self.bucket.object_exists(name)

    def size(self, name):
        file_info = self.get_file_header(name)
        return file_info.content_length

    def modified_time(self, name):
        file_info = self.get_file_header(name)
        return datetime.datetime.fromtimestamp(file_info.last_modified)

    def listdir(self, name):
        name = self._normalize_name(self._clean_name(name))
        if name and name.endswith('/'):
            name = name[:-1]

        files = []
        dirs = set()

        for obj in ObjectIterator(self.bucket, prefix=name, delimiter='/'):
            if obj.is_prefix():
                dirs.add(obj.key)
            else:
                files.append(obj.key)

        return list(dirs), files

    def url(self, name):
        name = self._normalize_name(self._clean_name(name))
        name = filepath_to_uri(name)
        return self.bucket._make_url(self.bucket_name, name)

    def read(self, name):
        pass

    def delete(self, name):
        pass
        # 不删除文件
        # name = self._get_target_name(name)
        # result = self.bucket.delete_object(name)
        # if result.status >= 400:
        # raise AliyunOperationError(result.resp)


@deconstructible
class OssThumbStorage(AliyunBaseStorage):
    """
    公共读的存储, 适用于封面图片等文件
    """
    acl = "public-read"
    bucket_name = settings.OSS_BUCKET.get("pic_bucket")
    """
    def get_oss_thumb_url(self, name, thumb_type='MID'):
        if settings.COVER_IMAGE_OSS_THUMB.get(thumb_type) is None:
            raise AliyunOperationError('could not find the thumb type {0} in settings'.format(thumb_type))
        return settings.COVER_IMAGE_OSS_THUMB.get(thumb_type).format(self.bucket_name, name)

    def url(self, name):
        return self.get_oss_thumb_url(name)
    """


@deconstructible
class OssPrivateStorage(AliyunBaseStorage):
    """
    私有bucket存储, 文件通过aes加密
    """
    acl = "private"
    bucket_name = settings.OSS_BUCKET.get("asset_bucket")
    encrypt = True



class AliyunFile(File):
    def __init__(self, name, storage, mode):
        self._storage = storage
        self._name = name[len(self._storage.location):]
        self._mode = mode
        self.file = six.BytesIO()
        self._is_dirty = False
        self._is_read = False
        super(AliyunFile, self).__init__(self.file, self._name)

    def read(self, num_bytes=None):
        # todo huge file
        if not self._is_read:
            if num_bytes is None:
                content = self._storage.bucket.get_object(self._name)
            else:
                content = self._storage.bucket.get_object(self._name, byte_range=(0, num_bytes))
            self.file = content
            self._is_read = True

        if 'b' in self._mode:
            return self.file
        else:
            return force_text(self.file)

    def write(self, content):
        #if 'w' not in self._mode:
        #    print self._mode
        #    raise AliyunOperationError("Operation write is not allowed.")

        self.file.write(force_bytes(content))
        self._is_dirty = True
        self._is_read = True

    def close(self):
        if self._is_dirty:
            self.file.seek(0)
            self._storage._save(self._name, self.file)
        self.file.close()