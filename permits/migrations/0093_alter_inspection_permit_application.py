# Generated by Django 4.1.7 on 2023-11-01 15:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0092_alter_inspection_inspecting_officer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspection',
            name='permit_application',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='permits.permitapplication'),
        ),
    ]