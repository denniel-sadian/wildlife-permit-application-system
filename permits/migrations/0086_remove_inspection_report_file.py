# Generated by Django 4.1.7 on 2023-10-22 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0085_alter_validation_permit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inspection',
            name='report_file',
        ),
    ]
