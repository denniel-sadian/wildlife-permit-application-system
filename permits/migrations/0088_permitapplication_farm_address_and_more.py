# Generated by Django 4.1.7 on 2023-10-25 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0087_permit_farm_address_permit_farm_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='permitapplication',
            name='farm_address',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='permitapplication',
            name='farm_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
