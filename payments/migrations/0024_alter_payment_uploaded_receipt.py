# Generated by Django 4.1.7 on 2023-11-09 02:41

from django.db import migrations, models
import users.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0023_alter_payment_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='uploaded_receipt',
            field=models.FileField(blank=True, null=True, upload_to='receipts/', validators=[users.mixins.validate_file_extension, users.mixins.validate_file_size]),
        ),
    ]
