# Generated by Django 5.1.2 on 2024-11-23 10:42

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("space_data", "0006_alter_image_url"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="payloadgroup",
            name="company",
        ),
    ]
