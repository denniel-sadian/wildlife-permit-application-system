# Generated by Django 4.1.7 on 2023-10-01 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0037_rename_requirement_uploadedrequirement'),
    ]

    operations = [
        migrations.CreateModel(
            name='Requirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, unique=True)),
                ('label', models.CharField(max_length=255)),
            ],
        ),
    ]