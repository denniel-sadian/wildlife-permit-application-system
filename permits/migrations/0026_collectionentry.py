# Generated by Django 4.1.7 on 2023-09-23 13:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0001_initial'),
        ('permits', '0025_permitapplication_names_and_addresses_of_authorized_collectors_or_trappers'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('permit_application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requested_animals', to='permits.permitapplication')),
                ('sub_species', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='animals.subspecies')),
                ('wcp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='allowed_animals', to='permits.wildlifecollectorpermit')),
            ],
            options={
                'unique_together': {('sub_species', 'permit_application')},
            },
        ),
    ]
