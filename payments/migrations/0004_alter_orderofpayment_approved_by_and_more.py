# Generated by Django 4.1.7 on 2023-09-27 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_remove_user_role'),
        ('permits', '0036_remove_oritem_order_of_payment_delete_orderofpayment_and_more'),
        ('payments', '0003_alter_orderofpayment_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderofpayment',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.admin'),
        ),
        migrations.AlterField(
            model_name='orderofpayment',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.client'),
        ),
        migrations.AlterField(
            model_name='orderofpayment',
            name='permit_application',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='permits.permitapplication'),
        ),
        migrations.AlterField(
            model_name='orderofpayment',
            name='prepared_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prepared_order_of_payments', to='users.admin'),
        ),
    ]
