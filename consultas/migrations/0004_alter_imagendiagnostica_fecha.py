# Generated by Django 5.0.7 on 2025-06-27 00:00

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultas', '0003_alter_imagendiagnostica_archivo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagendiagnostica',
            name='fecha',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
