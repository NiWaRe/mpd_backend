# Generated by Django 3.2.4 on 2021-06-28 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickstart', '0013_rename_remainingdosageinmg_patientownsmedication_daysleft'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='totalPriceInEUR',
            field=models.FloatField(),
        ),
    ]
