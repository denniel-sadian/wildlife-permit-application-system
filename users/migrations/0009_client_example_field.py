# Generated by Django 4.1.7 on 2023-08-20 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_permittee'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='example_field',
            field=models.CharField(default='example', max_length=50),
            preserve_default=False,
        ),
    ]
