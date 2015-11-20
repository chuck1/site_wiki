# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_auto_20151120_2122'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='shared_with_user',
            new_name='user_shared_with',
        ),
    ]
