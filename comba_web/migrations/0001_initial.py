# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CombaUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('user_role', models.CharField(default=b'SU', max_length=2, choices=[(b'admin', b'admin'), (b'serviceuser', b'Serviceuser'), (b'webuser', b'Webuser')])),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
