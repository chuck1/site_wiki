# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0008_auto_20160809_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskevent',
            name='event_type',
            field=models.IntegerField(choices=[(0, b'open'), (1, b'close'), (4, b'datetime start'), (2, b'datetime end'), (3, b'duration'), (5, b'precedent add'), (6, b'precedent remove')]),
        ),
    ]
