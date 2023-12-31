# Generated by Django 4.1.7 on 2023-08-20 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0001_initial'),
        ('permits', '0002_wildlifecollectorpermit_wildlifefarmpermit_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransportEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('ltp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='species_to_transport', to='permits.localtransportpermit')),
                ('sub_species', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transportings', to='animals.subspecies')),
            ],
        ),
        migrations.CreateModel(
            name='PermittedToCollectAnimal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('sub_species', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='species_permitted', to='animals.subspecies')),
                ('wcp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wcp_species', to='animals.subspecies')),
            ],
        ),
    ]
