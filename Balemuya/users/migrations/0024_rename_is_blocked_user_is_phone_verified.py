# Generated by Django 4.2.17 on 2025-04-04 11:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_rename_user_payment_customer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_blocked',
            new_name='is_phone_verified',
        ),
    ]
