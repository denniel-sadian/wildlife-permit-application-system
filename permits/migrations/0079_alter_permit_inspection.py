# Generated by Django 4.1.7 on 2023-10-21 08:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0078_alter_permit_payment_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permit',
            name='inspection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='permits.inspection'),
        ),
    ]
