# Generated by Django 5.1.7 on 2025-06-10 01:00

import django.core.validators
import django.db.models.deletion
import django_ckeditor_5.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Career',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(choices=[('Orthopaedic Specialist', 'Orthopaedic Specialist'), ('Prosthetist', 'Prosthetist'), ('Orthotist', 'Orthotist'), ('Physiotherapist (Orthopaedic Focused)', 'Physiotherapist (Orthopaedic Focused)'), ('Receptionist (Orthopaedic Medical)', 'Receptionist (Orthopaedic Medical)'), ('Marketing Specialist (Healthcare)', 'Marketing Specialist (Healthcare)'), ('Internship Opportunity (3 Months)', 'Internship Opportunity (3 Months)'), ('Other', 'Other')], max_length=200)),
                ('other_title', models.CharField(blank=True, max_length=200, null=True)),
                ('location', models.CharField(choices=[('Nairobi, Kenya', 'Nairobi, Kenya'), ('Other', 'Other')], max_length=100)),
                ('other_location', models.CharField(blank=True, max_length=100, null=True)),
                ('job_type', models.CharField(choices=[('Full-Time', 'Full-Time'), ('Part-Time', 'Part-Time'), ('Internship (3 Months)', 'Internship (3 Months)'), ('Cashual', 'Cashual')], max_length=50)),
                ('industry', models.CharField(choices=[('Healthcare / Orthopaedics', 'Healthcare / Orthopaedics'), ('Other', 'Other')], max_length=100)),
                ('other_industry', models.CharField(blank=True, max_length=100, null=True)),
                ('image_url', models.URLField(max_length=500)),
                ('about', django_ckeditor_5.fields.CKEditor5Field(verbose_name='About')),
                ('responsibilities', django_ckeditor_5.fields.CKEditor5Field(verbose_name='Responsibilities')),
                ('requirements', django_ckeditor_5.fields.CKEditor5Field(verbose_name='Requirements')),
                ('benefits', django_ckeditor_5.fields.CKEditor5Field(verbose_name='Benefits')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Careers',
            },
        ),
        migrations.CreateModel(
            name='CareerApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Phone must start with + and country code', regex='^\\+\\d{1,}$')])),
                ('job_title', models.CharField(max_length=100)),
                ('resume', models.FileField(upload_to='resumes/')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('career', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='careers.career')),
            ],
        ),
    ]
