# Generated by Django 4.2.17 on 2025-02-10 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0007_remove_servicebooking_agreed_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicepost',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('booked', 'booked'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='active', max_length=20),
        ),
    ]
