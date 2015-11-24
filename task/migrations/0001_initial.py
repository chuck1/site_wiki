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
                ('hide_children', models.BooleanField(default=False)),
                ('datetime_create', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, to='task.Task', null=True)),
                ('user_assign', models.ForeignKey(related_name='task_assign', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user_create', models.ForeignKey(related_name='task_create', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TaskEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_type', models.IntegerField(choices=[(0, b'open'), (1, b'close')])),
                ('event_datetime', models.DateTimeField(auto_now_add=True)),
                ('task', models.ForeignKey(to='task.Task')),
            ],
        ),
        migrations.CreateModel(
            name='TaskUserSharedWith',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task', models.ForeignKey(to='task.Task')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='user_shared_with',
            field=models.ManyToManyField(related_name='task_shared_with', through='task.TaskUserSharedWith', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
