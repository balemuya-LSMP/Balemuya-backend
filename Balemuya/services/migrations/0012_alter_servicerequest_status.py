# Generated by Django 4.2.17 on 2025-02-11 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_rename_details_servicerequest_detail_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('cancled', 'canceled'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
    ]
