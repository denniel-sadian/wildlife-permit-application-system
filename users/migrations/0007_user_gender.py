# Generated by Django 4.1.7 on 2023-03-25 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_is_initial_password_changed'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], default='N/A', max_length=10),
            preserve_default=False,
        ),
    ]
