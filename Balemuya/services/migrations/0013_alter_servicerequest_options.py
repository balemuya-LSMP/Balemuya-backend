# Generated by Django 4.2.17 on 2025-02-12 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0012_alter_servicerequest_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servicerequest',
            options={'ordering': ['-created_at'], 'verbose_name': 'Service Request', 'verbose_name_plural': 'Service Requests'},
        ),
    ]
