# Generated by Django 4.2.17 on 2025-02-04 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_alter_servicepost_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicepost',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
