# Generated by Django 4.1.7 on 2023-10-22 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0084_validation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validation',
            name='permit',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='permits.permit'),
        ),
    ]