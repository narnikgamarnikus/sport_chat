# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-26 15:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0003_message_team'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='team_left',
        ),
        migrations.RemoveField(
            model_name='event',
            name='team_right',
        ),
        migrations.AddField(
            model_name='event',
            name='away_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_away_team', to='chats.Team', verbose_name='Right team'),
        ),
        migrations.AddField(
            model_name='event',
            name='home_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_home_team', to='chats.Team', verbose_name='Left team'),
        ),
    ]
