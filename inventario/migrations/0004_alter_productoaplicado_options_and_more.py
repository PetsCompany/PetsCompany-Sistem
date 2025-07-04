# Generated by Django 5.0.7 on 2025-06-26 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0003_auto_20250625_1635'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productoaplicado',
            options={'ordering': ['-fecha_aplicacion', '-fecha_proxima'], 'verbose_name': 'Producto Aplicado', 'verbose_name_plural': 'Productos Aplicados'},
        ),
        migrations.AlterModelOptions(
            name='vacunaaplicada',
            options={'ordering': ['-fecha_aplicacion', '-fecha_proxima'], 'verbose_name': 'Vacuna Aplicada', 'verbose_name_plural': 'Vacunas Aplicadas'},
        ),
        migrations.AlterField(
            model_name='productoaplicado',
            name='fecha_aplicacion',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vacunaaplicada',
            name='fecha_aplicacion',
            field=models.DateField(blank=True, null=True),
        ),
    ]
