# Generated by Django 4.1.7 on 2023-10-07 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0012_rename_oritem_paymentorderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorder',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
