# Generated by Django 4.1.7 on 2023-03-25 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_client_address_alter_client_business_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_initial_password_changed',
            field=models.BooleanField(default=False),
        ),
    ]
