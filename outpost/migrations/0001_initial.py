# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Outpost',
            fields=[
                ('id', models.CharField(max_length=16, primary_key=True, serialize=False)),
            ],
        ),
    ]
