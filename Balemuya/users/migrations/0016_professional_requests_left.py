# Generated by Django 4.2.17 on 2025-02-12 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_feedback_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='requests_left',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
