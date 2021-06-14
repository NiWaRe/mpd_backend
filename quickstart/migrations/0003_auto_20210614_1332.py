# Generated by Django 3.2.4 on 2021-06-14 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickstart', '0002_doctors_inventory_patients_prescriptions_prescriptiontypes_userownsmedication'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='doctors',
            options={'verbose_name_plural': 'doctors'},
        ),
        migrations.AlterModelOptions(
            name='inventory',
            options={'verbose_name_plural': 'inventory'},
        ),
        migrations.AlterModelOptions(
            name='patients',
            options={'verbose_name_plural': 'patients'},
        ),
        migrations.AlterModelOptions(
            name='prescriptions',
            options={'verbose_name_plural': 'prescriptions'},
        ),
        migrations.AlterModelOptions(
            name='prescriptiontypes',
            options={'verbose_name_plural': 'prescription_types'},
        ),
        migrations.AlterModelOptions(
            name='userownsmedication',
            options={'verbose_name_plural': 'prescriptions'},
        ),
        migrations.AddField(
            model_name='inventory',
            name='ppPrice',
            field=models.IntegerField(default=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='doctors',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='imagePath',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='patients',
            name='condition',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='patients',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='prescriptions',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='prescriptiontypes',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='userownsmedication',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]