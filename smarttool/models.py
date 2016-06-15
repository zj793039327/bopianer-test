# encoding: utf-8

from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from core.basemodel import PrimaryKeyModel, Serializable
from core.code.bopianer_consts import *
from core.code.normalcode import *
from core.django_ext import OssPrivateStorage, OssThumbStorage


# Create your models here.
class Score(PrimaryKeyModel, Serializable):
    """
    音乐库:曲谱
    """

    class Meta:
        verbose_name = '曲谱'
        verbose_name_plural = '曲谱'
        db_table = 't_repo_score'

    version = models.CharField(max_length=20, blank=True, null=True, verbose_name='版本', db_column='c_version')
    name = models.CharField(max_length=300, blank=True, null=True, verbose_name='名称', db_column='c_name')
    desc = models.TextField(blank=True, null=True, verbose_name='演奏技巧', db_column='c_desc')
    status = models.IntegerField(blank=True, null=True, verbose_name='乐谱状态',
                                 choices=NormalCode.SCORE_STATUS, db_column='n_status_id')
    author = models.CharField(max_length=200, blank=True, null=True, verbose_name='作者', db_column='c_author')
    date_added = models.DateTimeField(default=timezone.now,
                                      verbose_name='创建日期',
                                      db_column='d_added')
    date_modified = models.DateTimeField(default=timezone.now, verbose_name='更新日期', db_column='d_modified')

    cover_pic_url = models.FileField(blank=True, null=True, db_column='c_cover_pic_url', verbose_name='封面图片',
                                     storage=OssThumbStorage())
    asset_pic_url = models.FileField(blank=True, null=True, db_column='c_asset_pic_url', verbose_name='曲谱内容图片l',
                                     storage=OssThumbStorage())
    asset_wechat_media_id = models.CharField(blank=True, null=True,
                                             max_length=200, db_column='c_asset_pic_wechat_media_id',
                                             verbose_name='曲谱内容图片所在微信服务器id')
    count_view = models.IntegerField(blank=True, null=True, db_column='n_count_view', verbose_name='查看人数')
    count_review = models.IntegerField(blank=True, null=True, db_column='n_count_review')
    openid = models.CharField(max_length=200, verbose_name='创建用户微信openid, 只有创建用户能编辑')

    def __unicode__(self):
        return '%s' % self.name


class ScoreWidget(PrimaryKeyModel, Serializable):
    class Meta:
        verbose_name = '曲谱小工具'
        verbose_name_plural = '曲谱小工具'
        db_table = 't_repo_score_widget'

    score = models.ForeignKey('Score', db_constraint=False, blank=False, null=False, db_column='c_score_id')
    top = models.DecimalField(verbose_name="工具左上角距离图片顶部百分比", db_column='n_top', max_digits=5, decimal_places=2)
    left = models.DecimalField(verbose_name="工具左上角距离图片左边百分比", db_column='n_left', max_digits=5, decimal_places=2)
    width = models.DecimalField(verbose_name="宽度", db_column='n_width', max_digits=5, decimal_places=2, default=1)
    height = models.DecimalField(verbose_name="高度", db_column='n_height', max_digits=5, decimal_places=2, default=1)
    type = models.IntegerField(db_column="n_type", choices=WIDGET_TYPE)
    content = models.TextField(db_column="c_content")
    date_added = models.DateTimeField(default=timezone.now,
                                      verbose_name='创建日期',
                                      db_column='d_added')
    voice_url = models.FileField(blank=True, null=True, db_column='c_voice_url', verbose_name='语音文件地址',
                                 storage=OssThumbStorage())
    voice_wechat_media_id = models.CharField(blank=True, null=True,
                                             max_length=200, db_column='c_voice_wechat_media_id',
                                             verbose_name='曲谱内容图片所在微信服务器id')


class Asset(PrimaryKeyModel, Serializable):
    """
    系统文件，文件的虚拟结构
    """
    physical_asset = models.ForeignKey('AssetPhysical', db_constraint=False, max_length=32, blank=True, null=True,
                                       db_column='c_asset_physical_id')
    name = models.CharField(max_length=200, blank=True, null=True, db_column='c_name')
    business_id = models.CharField(max_length=32, null=True, db_column='c_business_id', db_index=True)
    business_type = models.CharField(max_length=200, null=True, db_column='c_business_type')
    business_sort = models.IntegerField(null=True, db_column='n_business_sort')
    extension = models.CharField(max_length=200, blank=True, null=True, db_column='c_extension')
    date_added = models.DateTimeField(blank=True, null=True, default=timezone.now, db_column='d_added')

    class Meta:
        db_table = 't_sys_asset'

    def __unicode__(self):
        return self.name


class AssetPhysical(PrimaryKeyModel, Serializable):
    """
    文件的物理结构,实际的文件存储表
    """

    local_path = models.FileField(max_length=1000, blank=True, null=True, db_column='c_local_path',
                                  storage=OssPrivateStorage())
    # org_name
    name = models.CharField(max_length=200, blank=True, null=True, db_column='c_name')
    remote_url = models.CharField(max_length=200, blank=True, null=True, db_column='c_url')
    extension = models.CharField(max_length=200, blank=True, null=True, db_column='c_extension')
    date_added = models.DateTimeField(blank=True, null=True, default=timezone.now, db_column='d_added')
    date_download = models.DateTimeField(blank=True, null=True, db_column='d_download')
    byte_size = models.BigIntegerField(blank=True, null=True, db_column='n_byte_size')
    tag = models.CharField(max_length=200, blank=True, null=True, db_column='c_tag')
    oss_bucket = models.CharField(max_length=100, blank=False, null=True, db_column='c_oss_bucket')
    oss_endpoint = models.CharField(max_length=200, blank=False, null=True, db_column='c_oss_endpoint')
    oss_object = models.CharField(max_length=100, blank=False, null=True, db_column='c_oss_object')
    update_time = models.DateTimeField(blank=True, null=True, db_column='d_update')

    class Meta:
        db_table = 't_sys_asset_physical'
