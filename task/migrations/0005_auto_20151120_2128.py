# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0004_auto_20151120_2122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='user_assign',
            field=models.ForeignKey(related_name='tasks_assign', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
