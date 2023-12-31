# Generated by Django 4.1.7 on 2023-09-26 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0014_remove_user_role'),
        ('permits', '0036_remove_oritem_order_of_payment_delete_orderofpayment_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderOfPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no', models.CharField(max_length=255)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('nature_of_doc_being_secured', models.CharField(max_length=255, verbose_name='Nature of Application/Permit/Documents being secured')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ors_3', to='users.admin')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ors', to='users.client')),
                ('permit_application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ors_1', to='permits.permitapplication', unique=True)),
                ('prepared_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ors_2', to='users.admin')),
            ],
        ),
        migrations.CreateModel(
            name='ORItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('legal_basis', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order_of_payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='payments.orderofpayment')),
            ],
            options={
                'verbose_name': 'Order of Payment Item',
            },
        ),
    ]
