# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sheet',
            name='port',
            field=models.IntegerField(default=-1),
        ),
    ]
