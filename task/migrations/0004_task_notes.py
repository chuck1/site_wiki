# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_task_bool_wait_for_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='notes',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
