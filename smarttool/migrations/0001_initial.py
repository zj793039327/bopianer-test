# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-12 00:28
from __future__ import unicode_literals

import core.basemodel
import core.django_ext
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.CharField(db_column=b'c_id', default=core.basemodel._unique, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, db_column='c_name', max_length=200, null=True)),
                ('business_id', models.CharField(db_column='c_business_id', db_index=True, max_length=32, null=True)),
                ('business_type', models.CharField(db_column='c_business_type', max_length=200, null=True)),
                ('business_sort', models.IntegerField(db_column='n_business_sort', null=True)),
                ('extension', models.CharField(blank=True, db_column='c_extension', max_length=200, null=True)),
                ('date_added', models.DateTimeField(blank=True, db_column='d_added', default=django.utils.timezone.now, null=True)),
            ],
            options={
                'db_table': 't_sys_asset',
            },
            bases=(models.Model, core.basemodel.Serializable),
        ),
        migrations.CreateModel(
            name='AssetPhysical',
            fields=[
                ('id', models.CharField(db_column=b'c_id', default=core.basemodel._unique, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('local_path', models.FileField(blank=True, db_column='c_local_path', max_length=1000, null=True, storage=core.django_ext.OssPrivateStorage(), upload_to=b'')),
                ('name', models.CharField(blank=True, db_column='c_name', max_length=200, null=True)),
                ('remote_url', models.CharField(blank=True, db_column='c_url', max_length=200, null=True)),
                ('extension', models.CharField(blank=True, db_column='c_extension', max_length=200, null=True)),
                ('date_added', models.DateTimeField(blank=True, db_column='d_added', default=django.utils.timezone.now, null=True)),
                ('date_download', models.DateTimeField(blank=True, db_column='d_download', null=True)),
                ('byte_size', models.BigIntegerField(blank=True, db_column='n_byte_size', null=True)),
                ('tag', models.CharField(blank=True, db_column='c_tag', max_length=200, null=True)),
                ('oss_bucket', models.CharField(db_column='c_oss_bucket', max_length=100, null=True)),
                ('oss_endpoint', models.CharField(db_column='c_oss_endpoint', max_length=200, null=True)),
                ('oss_object', models.CharField(db_column='c_oss_object', max_length=100, null=True)),
                ('update_time', models.DateTimeField(blank=True, db_column='d_update', null=True)),
            ],
            options={
                'db_table': 't_sys_asset_physical',
            },
            bases=(models.Model, core.basemodel.Serializable),
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.CharField(db_column=b'c_id', default=core.basemodel._unique, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('version', models.CharField(blank=True, db_column='c_version', max_length=20, null=True, verbose_name='\u7248\u672c')),
                ('name', models.CharField(blank=True, db_column='c_name', max_length=300, null=True, verbose_name='\u540d\u79f0')),
                ('desc', models.TextField(blank=True, db_column='c_desc', null=True, verbose_name='\u6f14\u594f\u6280\u5de7')),
                ('status', models.IntegerField(blank=True, choices=[(10, b'\xe5\xaf\xbc\xe5\x85\xa5'), (20, b'\xe5\xb7\xb2\xe6\xa0\xa1\xe5\xaf\xb9'), (30, b'\xe5\xb7\xb2\xe5\xae\xa1\xe6\xa0\xb8'), (40, b'\xe5\xb7\xb2\xe6\x94\xb9\xe8\x89\xaf')], db_column='n_status_id', null=True, verbose_name='\u4e50\u8c31\u72b6\u6001')),
                ('author', models.CharField(blank=True, db_column='c_author', max_length=200, null=True, verbose_name='\u4f5c\u8005')),
                ('date_added', models.DateTimeField(db_column='d_added', default=django.utils.timezone.now, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('date_modified', models.DateTimeField(db_column='d_modified', default=django.utils.timezone.now, verbose_name='\u66f4\u65b0\u65e5\u671f')),
                ('cover_pic_url', models.FileField(blank=True, db_column='c_cover_pic_url', null=True, storage=core.django_ext.OssThumbStorage(), upload_to=b'', verbose_name='\u5c01\u9762\u56fe\u7247')),
                ('asset_pic_url', models.FileField(blank=True, db_column='c_asset_pic_url', null=True, storage=core.django_ext.OssThumbStorage(), upload_to=b'', verbose_name='\u66f2\u8c31\u5185\u5bb9\u56fe\u7247l')),
                ('count_view', models.IntegerField(blank=True, db_column='n_count_view', null=True, verbose_name='\u67e5\u770b\u4eba\u6570')),
                ('count_review', models.IntegerField(blank=True, db_column='n_count_review', null=True)),
                ('openid', models.CharField(max_length=200, verbose_name='\u521b\u5efa\u7528\u6237\u5fae\u4fe1openid, \u53ea\u6709\u521b\u5efa\u7528\u6237\u80fd\u7f16\u8f91')),
            ],
            options={
                'db_table': 't_repo_score',
                'verbose_name': '\u66f2\u8c31',
                'verbose_name_plural': '\u66f2\u8c31',
            },
            bases=(models.Model, core.basemodel.Serializable),
        ),
        migrations.CreateModel(
            name='ScoreWidget',
            fields=[
                ('id', models.CharField(db_column=b'c_id', default=core.basemodel._unique, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('top', models.DecimalField(db_column='n_top', decimal_places=2, max_digits=5, verbose_name='\u5de5\u5177\u5de6\u4e0a\u89d2\u8ddd\u79bb\u56fe\u7247\u9876\u90e8\u767e\u5206\u6bd4')),
                ('left', models.DecimalField(db_column='n_left', decimal_places=2, max_digits=5, verbose_name='\u5de5\u5177\u5de6\u4e0a\u89d2\u8ddd\u79bb\u56fe\u7247\u5de6\u8fb9\u767e\u5206\u6bd4')),
                ('width', models.DecimalField(db_column='n_width', decimal_places=2, max_digits=5, verbose_name='\u5bbd\u5ea6')),
                ('height', models.DecimalField(db_column='n_height', decimal_places=2, max_digits=5, verbose_name='\u9ad8\u5ea6')),
                ('type', models.IntegerField(choices=[(1, b'\xe8\xaf\xad\xe9\x9f\xb3'), (2, b'\xe6\x96\x87\xe5\xad\x97')], db_column='n_type', max_length=5)),
                ('content', models.TextField(db_column='c_content')),
                ('voice_url', models.CharField(db_column='c_voice_url', max_length=500)),
                ('score', models.ForeignKey(db_column='c_score_id', db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='smarttool.Score')),
            ],
            options={
                'db_table': 't_repo_score_widget',
                'verbose_name': '\u66f2\u8c31\u5c0f\u5de5\u5177',
                'verbose_name_plural': '\u66f2\u8c31\u5c0f\u5de5\u5177',
            },
            bases=(models.Model, core.basemodel.Serializable),
        ),
        migrations.AddField(
            model_name='asset',
            name='physical_asset',
            field=models.ForeignKey(blank=True, db_column='c_asset_physical_id', db_constraint=False, max_length=32, null=True, on_delete=django.db.models.deletion.CASCADE, to='smarttool.AssetPhysical'),
        ),
    ]
