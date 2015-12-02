# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0004_auto_20151202_2057'),
    ]

    operations = [
        migrations.AddField(
            model_name='mygroup',
            name='name',
            field=models.CharField(default='none', max_length=256),
            preserve_default=False,
        ),
    ]
