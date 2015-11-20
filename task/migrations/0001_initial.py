# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('create_user', models.ForeignKey(related_name='tasks_created', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(to='task.Task')),
                ('shared_with_user', models.ManyToManyField(related_name='tasks_shared_with', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
