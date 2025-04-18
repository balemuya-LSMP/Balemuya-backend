# Generated by Django 4.2.17 on 2025-02-11 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_alter_complain_message'),
    ]

    operations = [
        migrations.RenameField(
            model_name='servicerequest',
            old_name='details',
            new_name='detail',
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('cancled', 'canceled'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], max_length=20),
        ),
    ]
