# Generated by Django 4.1.7 on 2023-10-07 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0055_signature'),
    ]

    operations = [
        migrations.AddField(
            model_name='signature',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
