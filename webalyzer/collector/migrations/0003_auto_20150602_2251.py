# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0002_stylesheet'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='html_hash',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='stylesheet',
            name='html_hash',
            field=models.IntegerField(default=0),
        ),
    ]
