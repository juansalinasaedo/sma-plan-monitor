# Generated by Django 5.1.7 on 2025-04-09 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportegenerado',
            name='activo',
            field=models.BooleanField(default=True, verbose_name='Activo'),
        ),
    ]
