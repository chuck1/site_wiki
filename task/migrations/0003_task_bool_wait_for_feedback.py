# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_task_priority'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='bool_wait_for_feedback',
            field=models.BooleanField(default=False),
        ),
    ]
