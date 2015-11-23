# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0009_task_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='hide_children',
            field=models.BooleanField(default=False),
        ),
    ]
