# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0008_auto_20151120_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='status',
            field=models.CharField(default=b'ST', max_length=2, blank=True, choices=[(b'ST', b'started'), (b'CO', b'completed'), (b'CA', b'cancelled')]),
        ),
    ]
