# Generated by Django 3.1.4 on 2024-05-25 01:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_job_year_of_filling'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='KRA_password',
            new_name='kra_password',
        ),
    ]