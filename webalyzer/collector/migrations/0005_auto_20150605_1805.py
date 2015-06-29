# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0004_auto_20150604_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='source_hash',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AlterField(
            model_name='stylesheet',
            name='source_hash',
            field=models.IntegerField(default=0, db_index=True),
        ),
    ]
