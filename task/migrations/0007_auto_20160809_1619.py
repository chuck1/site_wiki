# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0006_task_precedents'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskevent',
            name='duration',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='taskevent',
            name='event_type',
            field=models.IntegerField(choices=[(0, b'open'), (1, b'close'), (2, b'datetime end'), (3, b'duration')]),
        ),
    ]
