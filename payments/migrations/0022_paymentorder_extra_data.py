# Generated by Django 4.1.7 on 2023-10-29 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0021_alter_payment_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorder',
            name='extra_data',
            field=models.JSONField(default=dict),
        ),
    ]