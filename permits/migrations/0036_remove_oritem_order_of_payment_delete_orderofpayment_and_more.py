# Generated by Django 4.1.7 on 2023-09-26 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0035_orderofpayment_oritem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oritem',
            name='order_of_payment',
        ),
        migrations.DeleteModel(
            name='OrderOfPayment',
        ),
        migrations.DeleteModel(
            name='ORItem',
        ),
    ]
