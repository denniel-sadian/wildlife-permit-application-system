# Generated by Django 4.1.7 on 2023-10-07 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_signatory'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='signatory',
            options={'verbose_name': 'Signatory', 'verbose_name_plural': 'Signatories'},
        ),
    ]
