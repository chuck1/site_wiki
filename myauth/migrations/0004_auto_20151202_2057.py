# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0003_auto_20151202_1817'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Group',
            new_name='MyGroup',
        ),
    ]
