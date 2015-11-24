# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0010_task_hide_children'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_type', models.IntegerField(choices=[(0, b'open'), (1, b'close')])),
                ('event_datetime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='datetime_create',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 24, 0, 10, 14, 977573, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskevent',
            name='task',
            field=models.ForeignKey(to='task.Task'),
        ),
    ]
