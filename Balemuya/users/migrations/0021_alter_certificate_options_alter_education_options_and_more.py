# Generated by Django 4.2.17 on 2025-04-04 10:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_alter_user_options_remove_user_date_joined_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='certificate',
            options={'ordering': ['-created_at'], 'verbose_name': 'Certificate', 'verbose_name_plural': 'Certificates'},
        ),
        migrations.AlterModelOptions(
            name='education',
            options={'ordering': ['-created_at'], 'verbose_name': 'Education', 'verbose_name_plural': 'Educations'},
        ),
        migrations.RenameField(
            model_name='subscriptionplan',
            old_name='professional',
            new_name='user',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_organization',
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(choices=[('subscription', 'Subscription'), ('transaction', 'Transaction')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='account_type',
            field=models.CharField(choices=[('organization', 'Organization'), ('individual', 'Individual')], default='ind', max_length=30),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='education',
            name='professional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='payment',
            name='professional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_payments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='payment',
            name='subscription_plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='users.subscriptionplan'),
        ),
        migrations.AlterField(
            model_name='verificationrequest',
            name='verified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verifications', to=settings.AUTH_USER_MODEL),
        ),
    ]
