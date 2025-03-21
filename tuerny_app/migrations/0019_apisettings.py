# Generated by Django 5.1.5 on 2025-02-05 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tuerny_app', '0018_categorysuggestedblog'),
    ]

    operations = [
        migrations.CreateModel(
            name='APISettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='API Adı (Örn: Google Analytics)', max_length=255, unique=True)),
                ('script', models.TextField(help_text='Tam script kodunu buraya girin')),
                ('is_active', models.BooleanField(default=True, help_text="API'yi aktif/pasif yap")),
            ],
        ),
    ]
