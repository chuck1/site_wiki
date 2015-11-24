# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0011_auto_20151124_0010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='status',
        ),
    ]
