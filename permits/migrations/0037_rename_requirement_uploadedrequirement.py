# Generated by Django 4.1.7 on 2023-10-01 13:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0036_remove_oritem_order_of_payment_delete_orderofpayment_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Requirement',
            new_name='UploadedRequirement',
        ),
    ]