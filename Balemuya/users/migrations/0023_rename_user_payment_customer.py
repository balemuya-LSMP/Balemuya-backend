# Generated by Django 4.2.17 on 2025-04-04 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_user_is_email_verified'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='user',
            new_name='customer',
        ),
    ]
