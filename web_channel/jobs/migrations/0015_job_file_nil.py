# Generated by Django 3.1.4 on 2024-06-13 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0014_job_screenshot_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='file_nil',
            field=models.BooleanField(default=False),
        ),
    ]
