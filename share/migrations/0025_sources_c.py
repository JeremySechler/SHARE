# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-03-03 19:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0024_sources_b'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RawData',
            new_name='RawDatum',
        ),
        migrations.AlterField(
            model_name='rawdatum',
            name='suid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='share.SourceUniqueIdentifier'),
        ),
        migrations.AlterUniqueTogether(
            name='rawdatum',
            unique_together=set([('suid', 'sha256')]),
        ),
        migrations.RemoveField(
            model_name='rawdatum',
            name='app_label',
        ),
        migrations.RemoveField(
            model_name='rawdatum',
            name='provider_doc_id',
        ),
        migrations.RemoveField(
            model_name='rawdatum',
            name='source',
        ),
        migrations.RenameField(
            model_name='rawdatum',
            old_name='data',
            new_name='datum',
        ),
        migrations.RenameField(
            model_name='rawdatum',
            old_name='date_harvested',
            new_name='date_created',
        ),
        migrations.RenameField(
            model_name='rawdatum',
            old_name='date_seen',
            new_name='date_modified',
        ),
    ]