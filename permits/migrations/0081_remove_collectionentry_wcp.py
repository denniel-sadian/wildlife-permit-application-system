# Generated by Django 4.1.7 on 2023-10-21 10:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0080_alter_collectionentry_wcp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collectionentry',
            name='wcp',
        ),
    ]