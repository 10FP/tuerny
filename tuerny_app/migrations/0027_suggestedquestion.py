# Generated by Django 5.1.5 on 2025-02-26 02:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tuerny_app', '0026_subcategory_saved_users'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuggestedQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('question', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='suggested_question', to='tuerny_app.question')),
            ],
        ),
    ]
