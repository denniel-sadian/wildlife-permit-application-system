# Generated by Django 4.1.7 on 2023-10-07 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0060_alter_permitapplication_permit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transportentry',
            name='ltp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='species_to_transport', to='permits.localtransportpermit'),
        ),
    ]
