# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myauth', '0004_auto_20151202_2057'),
        ('wiki', '0008_patch_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageGroupEdit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(to='myauth.MyGroup')),
            ],
        ),
        migrations.CreateModel(
            name='PageGroupView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(to='myauth.MyGroup')),
            ],
        ),
        migrations.CreateModel(
            name='PageUserEdit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='PageUserView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='page',
            name='user_create',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='path',
            field=models.CharField(max_length=1000),
        ),
        migrations.AddField(
            model_name='pageuserview',
            name='page',
            field=models.ForeignKey(to='wiki.Page'),
        ),
        migrations.AddField(
            model_name='pageuserview',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pageuseredit',
            name='page',
            field=models.ForeignKey(to='wiki.Page'),
        ),
        migrations.AddField(
            model_name='pageuseredit',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pagegroupview',
            name='page',
            field=models.ForeignKey(to='wiki.Page'),
        ),
        migrations.AddField(
            model_name='pagegroupedit',
            name='page',
            field=models.ForeignKey(to='wiki.Page'),
        ),
        migrations.AddField(
            model_name='page',
            name='groups_edit',
            field=models.ManyToManyField(related_name='page_groups_edit', through='wiki.PageGroupEdit', to='myauth.MyGroup', blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='groups_view',
            field=models.ManyToManyField(related_name='page_groups_view', through='wiki.PageGroupView', to='myauth.MyGroup', blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='users_edit',
            field=models.ManyToManyField(related_name='page_users_edit', through='wiki.PageUserEdit', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='users_view',
            field=models.ManyToManyField(related_name='page_users_view', through='wiki.PageUserView', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
