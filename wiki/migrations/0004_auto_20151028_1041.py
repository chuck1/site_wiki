# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_branch'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orig', models.TextField()),
                ('page', models.ForeignKey(to='wiki.Page')),
            ],
        ),
        migrations.DeleteModel(
            name='Branch',
        ),
    ]
