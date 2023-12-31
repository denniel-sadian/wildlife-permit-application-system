# Generated by Django 4.1.7 on 2023-10-07 11:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0057_transportentry_description_and_more'),
        ('payments', '0013_paymentorder_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentorder',
            name='permit_application',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='permits.permitapplication'),
        ),
    ]
