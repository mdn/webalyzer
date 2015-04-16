# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Screenshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', sorl.thumbnail.fields.ImageField(upload_to=b'screenshots')),
                ('width', models.PositiveIntegerField()),
                ('height', models.PositiveIntegerField()),
                ('engine', models.CharField(default=b'slimerjs', max_length=100)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('page', models.ForeignKey(to='collector.Page')),
            ],
        ),
    ]
