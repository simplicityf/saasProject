# Generated by Django 5.1.2 on 2024-11-19 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('subscriptions', '0002_subcription_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcription',
            name='permission',
            field=models.ManyToManyField(limit_choices_to={'content_type__app_label': 'subscriptions'}, to='auth.permission'),
        ),
    ]