# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_auto_20151120_2116'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='assign_user',
            new_name='user_assign',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='create_user',
            new_name='user_create',
        ),
    ]
