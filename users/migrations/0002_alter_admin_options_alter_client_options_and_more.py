# Generated by Django 4.1.7 on 2023-03-25 05:05

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='admin',
            options={'verbose_name': 'Admin'},
        ),
        migrations.AlterModelOptions(
            name='client',
            options={'verbose_name': 'Client'},
        ),
        migrations.RemoveField(
            model_name='client',
            name='contact_number',
        ),
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=14, region=None),
        ),
    ]
