# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(verbose_name='body')),
                ('sent_at', models.DateTimeField(auto_now_add=True, verbose_name='sent at', db_index=True)),
                ('parent_msg', models.ForeignKey(related_name='next_messages', verbose_name='parent message', blank=True, to='threaded_messages.Message', null=True)),
                ('sender', models.ForeignKey(related_name='sent_messages', verbose_name='sender', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-sent_at'],
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('read_at', models.DateTimeField(db_index=True, null=True, verbose_name='read at', blank=True)),
                ('replied_at', models.DateTimeField(db_index=True, null=True, verbose_name='replied at', blank=True)),
                ('deleted_at', models.DateTimeField(db_index=True, null=True, verbose_name='deleted at', blank=True)),
            ],
            options={
                'ordering': ['thread'],
                'verbose_name': 'participant',
                'verbose_name_plural': 'participants',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=120, verbose_name='Subject')),
                ('replied', models.BooleanField(default=False, editable=False)),
                ('all_msgs', models.ManyToManyField(related_name='thread', verbose_name='Messages', to='threaded_messages.Message')),
                ('creator', models.ForeignKey(related_name='created_threads', verbose_name='creator', to=settings.AUTH_USER_MODEL)),
                ('latest_msg', models.ForeignKey(related_name='thread_latest', verbose_name='Latest message', to='threaded_messages.Message')),
            ],
            options={
                'ordering': ['latest_msg'],
                'verbose_name': 'Thread',
                'verbose_name_plural': 'Threads',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='participant',
            name='thread',
            field=models.ForeignKey(related_name='participants', verbose_name='message thread', to='threaded_messages.Thread'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='participant',
            name='user',
            field=models.ForeignKey(related_name='threads', verbose_name='participant users', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
