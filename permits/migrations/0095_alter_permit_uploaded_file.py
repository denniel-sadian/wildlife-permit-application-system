# Generated by Django 4.1.7 on 2023-11-01 16:40

from django.db import migrations, models
import users.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0094_permit_or_no_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permit',
            name='uploaded_file',
            field=models.FileField(null=True, upload_to='uploads/', validators=[users.mixins.validate_file_extension]),
        ),
    ]
