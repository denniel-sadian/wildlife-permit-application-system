# Generated by Django 4.1.7 on 2023-09-20 09:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0020_alter_requirementitem_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='requirementitem',
            unique_together={('requirement_list', 'requirement')},
        ),
    ]
