# Generated by Django 4.1.7 on 2024-02-29 02:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0103_alter_permitapplication_inspection_report'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inspection',
            name='inspecting_officer',
        ),
    ]
