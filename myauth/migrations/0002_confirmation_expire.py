# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmation',
            name='expire',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 25, 16, 2, 24, 242145, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
