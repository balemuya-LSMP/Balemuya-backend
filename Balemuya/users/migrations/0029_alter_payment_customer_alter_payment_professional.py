# Generated by Django 4.2.17 on 2025-04-12 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_remove_orgprofessional_categories_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_payments', to='users.customer'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='professional',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_payments', to='users.professional'),
        ),
    ]
