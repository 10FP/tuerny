# Generated by Django 5.1.5 on 2025-01-31 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tuerny_app', '0016_suggestedblog'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='extra_categories',
            field=models.ManyToManyField(blank=True, related_name='extra_blogs', to='tuerny_app.subcategory'),
        ),
    ]
