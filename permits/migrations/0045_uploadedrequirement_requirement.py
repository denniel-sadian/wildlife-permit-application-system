# Generated by Django 4.1.7 on 2023-10-01 14:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0044_alter_uploadedrequirement_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedrequirement',
            name='requirement',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='permits.requirement'),
            preserve_default=False,
        ),
    ]
