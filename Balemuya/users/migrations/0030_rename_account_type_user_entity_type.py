# Generated by Django 4.2.17 on 2025-04-12 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_alter_payment_customer_alter_payment_professional'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='account_type',
            new_name='entity_type',
        ),
    ]
