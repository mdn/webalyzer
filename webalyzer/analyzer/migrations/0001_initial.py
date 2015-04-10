# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=100, db_index=True)),
                ('url', models.URLField()),
                ('line', models.PositiveIntegerField(null=True)),
                ('before', models.TextField()),
                ('after', models.TextField()),
                ('ignored', models.BooleanField(default=False)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Suspect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('selector', models.TextField()),
                ('selector_full', models.TextField()),
                ('style', models.TextField()),
                ('line', models.PositiveIntegerField(null=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('result', models.ForeignKey(to='analyzer.Result')),
            ],
            options={
                'ordering': ('modified',),
            },
        ),
    ]
