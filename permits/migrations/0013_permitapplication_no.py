# Generated by Django 4.1.7 on 2023-09-13 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0012_alter_requirement_requirement_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='permitapplication',
            name='no',
            field=models.CharField(default='here', max_length=255),
            preserve_default=False,
        ),
    ]
