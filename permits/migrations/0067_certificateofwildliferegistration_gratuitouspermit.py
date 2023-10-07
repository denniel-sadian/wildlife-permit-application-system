# Generated by Django 4.1.7 on 2023-10-07 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0066_alter_permit_permittee'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateOfWildlifeRegistration',
            fields=[
                ('permit_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='permits.permit')),
            ],
            bases=('permits.permit',),
        ),
        migrations.CreateModel(
            name='GratuitousPermit',
            fields=[
                ('permit_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='permits.permit')),
            ],
            bases=('permits.permit',),
        ),
    ]
