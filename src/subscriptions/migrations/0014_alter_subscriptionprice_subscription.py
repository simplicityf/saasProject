# Generated by Django 5.1.2 on 2024-12-13 07:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0013_alter_subscription_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionprice',
            name='subscription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='subscriptions.subscription'),
        ),
    ]
