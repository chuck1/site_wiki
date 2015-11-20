# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0006_auto_20151120_2130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='user_shared_with',
            field=models.ManyToManyField(related_name='tasks_shared_with', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
