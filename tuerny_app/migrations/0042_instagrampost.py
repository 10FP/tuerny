# Generated by Django 5.0.1 on 2025-03-30 20:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tuerny_app', '0041_blog_views_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255)),
                ('image', models.ImageField(upload_to='instagram/')),
                ('caption', models.TextField(blank=True)),
                ('post_url', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
