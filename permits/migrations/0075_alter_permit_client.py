# Generated by Django 4.1.7 on 2023-10-14 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_delete_permittee'),
        ('permits', '0074_remove_permit_permittee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permit',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='permits', to='users.client'),
        ),
    ]
