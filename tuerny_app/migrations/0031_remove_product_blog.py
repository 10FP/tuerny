# Generated by Django 5.1.5 on 2025-03-05 23:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tuerny_app', '0030_remove_blog_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='blog',
        ),
    ]
