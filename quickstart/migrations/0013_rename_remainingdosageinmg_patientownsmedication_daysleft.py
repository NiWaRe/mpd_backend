# Generated by Django 3.2.4 on 2021-06-28 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quickstart', '0012_alter_prescriptions_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patientownsmedication',
            old_name='remainingDosageInMg',
            new_name='daysLeft',
        ),
    ]