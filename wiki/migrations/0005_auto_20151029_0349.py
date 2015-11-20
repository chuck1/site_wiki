# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0004_auto_20151028_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='patch',
            name='commit_edit',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patch',
            name='commit_orig',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
