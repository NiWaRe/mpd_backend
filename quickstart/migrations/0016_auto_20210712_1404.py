# Generated by Django 3.2.4 on 2021-07-12 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickstart', '0015_patientownsmedication_totaldays'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctors',
            name='email',
            field=models.CharField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='patients',
            name='email',
            field=models.CharField(max_length=10000),
        ),
    ]
