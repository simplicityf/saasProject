# Generated by Django 5.1.2 on 2024-11-19 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('subscriptions', '0003_subcription_permission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcription',
            name='permission',
            field=models.ManyToManyField(limit_choices_to={'codename__in': ['advance pro', 'advance', 'basic', 'free'], 'content_type__app_label': 'subscriptions'}, to='auth.permission'),
        ),
    ]
