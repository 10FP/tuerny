# Generated by Django 5.1.5 on 2025-02-16 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tuerny_app', '0019_apisettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='topic',
            field=models.CharField(blank=True, choices=[('destek', 'Destek Talebi'), ('oneri', 'Öneri'), ('sikayet', 'Şikayet'), ('diger', 'Diğer')], max_length=20, null=True, verbose_name='Konu'),
        ),
    ]
