# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0009_auto_20151202_2100'),
    ]

    operations = [
        migrations.AddField(
            model_name='patch',
            name='datetime_create',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 9, 21, 22, 55, 150756, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
