# Generated by Django 4.1.7 on 2023-10-01 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0042_rename_requirement_fk_requirementitem_requirement'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='requirementitem',
            unique_together={('requirement_list', 'requirement')},
        ),
    ]