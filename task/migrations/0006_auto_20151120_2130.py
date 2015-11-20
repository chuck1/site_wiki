# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0005_auto_20151120_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='parent',
            field=models.ForeignKey(blank=True, to='task.Task', null=True),
        ),
    ]
