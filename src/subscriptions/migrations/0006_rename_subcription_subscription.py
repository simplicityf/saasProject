# Generated by Django 5.1.2 on 2024-11-19 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('subscriptions', '0005_subcription_active'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Subcription',
            new_name='Subscription',
        ),
    ]