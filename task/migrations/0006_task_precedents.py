# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0005_auto_20160406_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='precedents',
            field=models.ManyToManyField(related_name='task_precedents', null=True, to='task.Task'),
        ),
    ]
