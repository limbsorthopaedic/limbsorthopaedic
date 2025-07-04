# Generated by Django 5.1.7 on 2025-06-10 01:05

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Staff Group',
                'verbose_name_plural': 'Staff Groups',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StaffChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_system_message', models.BooleanField(default=False, help_text='System messages are displayed differently')),
                ('is_edited', models.BooleanField(default=False, help_text='Shows if the message has been edited')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_staff_messages', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='staff_chat.staffgroup')),
            ],
            options={
                'verbose_name': 'Staff Chat Message',
                'verbose_name_plural': 'Staff Chat Messages',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='staff_chat_attachments/')),
                ('file_name', models.CharField(blank=True, max_length=255)),
                ('file_type', models.CharField(blank=True, max_length=100)),
                ('file_size', models.PositiveIntegerField(default=0, help_text='File size in bytes')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='staff_chat.staffchatmessage')),
            ],
            options={
                'verbose_name': 'Chat Attachment',
                'verbose_name_plural': 'Chat Attachments',
                'ordering': ['uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='StaffGroupMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False, help_text='Admin members can manage the group')),
                ('is_active', models.BooleanField(default=True, help_text="Inactive members won't receive notifications")),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('last_read_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='staff_chat.staffgroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Staff Group Member',
                'verbose_name_plural': 'Staff Group Members',
                'ordering': ['group', 'user__username'],
                'unique_together': {('user', 'group')},
            },
        ),
    ]
