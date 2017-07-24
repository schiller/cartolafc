# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_partida_rodada'),
    ]

    operations = [
        migrations.CreateModel(
            name='Atleta',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=200)),
                ('apelido', models.CharField(max_length=200)),
                ('foto', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Posicao',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=20)),
                ('abreviacao', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=20)),
            ],
        ),
    ]
