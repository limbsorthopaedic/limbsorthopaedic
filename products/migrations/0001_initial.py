# Generated by Django 5.1.7 on 2025-06-10 00:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomProductRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('details', models.TextField(help_text='Details about the custom product needed')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('admin_notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Custom Product Request',
                'verbose_name_plural': 'Custom Product Requests',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(unique=True)),
                ('order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Product Categories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField()),
                ('price', models.DecimalField(blank=True, decimal_places=2, help_text='Leave empty if price varies or is available on request', max_digits=10, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('image_url', models.URLField(blank=True, help_text='Optional external URL for image (used if no image is uploaded)', max_length=500, null=True)),
                ('featured', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.productcategory')),
            ],
            options={
                'ordering': ['order', 'title'],
            },
        ),
    ]
