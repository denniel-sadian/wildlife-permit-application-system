# Generated by Django 4.1.7 on 2023-09-30 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0036_remove_oritem_order_of_payment_delete_orderofpayment_and_more'),
        ('payments', '0005_payment_payment_payments_pa_related_1d6af5_idx'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='payment',
            name='payments_pa_related_1d6af5_idx',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='related_object_id',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='related_object_type',
        ),
        migrations.AlterField(
            model_name='payment',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='permits.permitapplication'),
        ),
    ]
