# Generated by Django 3.1.4 on 2024-06-20 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_auto_20240620_0854'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='has_tax_obligations',
            field=models.BooleanField(default=False),
        ),
    ]
