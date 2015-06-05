# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0003_auto_20150602_2251'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='html_hash',
            new_name='source_hash',
        ),
        migrations.RenameField(
            model_name='stylesheet',
            old_name='html_hash',
            new_name='source_hash',
        ),
    ]
