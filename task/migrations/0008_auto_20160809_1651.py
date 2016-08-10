# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0007_auto_20160809_1619'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='precedents',
        ),
        migrations.AddField(
            model_name='taskevent',
            name='precedent',
            field=models.ForeignKey(related_name='taskevent_precedent', to='task.Task', null=True),
        ),
    ]
