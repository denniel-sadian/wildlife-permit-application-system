# Generated by Django 4.1.7 on 2023-09-10 07:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_permittee_farm_address_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
    ]
