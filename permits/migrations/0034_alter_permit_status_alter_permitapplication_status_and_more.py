# Generated by Django 4.1.7 on 2023-09-26 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0033_alter_remarks_options_remarks_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permit',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'On Draft'), ('SUBMITTED', 'Submitted'), ('RETURNED', 'Returned'), ('ACCEPTED', 'Accepted'), ('RELEASED', 'Released'), ('EXPIRED', 'Expired')], max_length=50),
        ),
        migrations.AlterField(
            model_name='permitapplication',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'On Draft'), ('SUBMITTED', 'Submitted'), ('RETURNED', 'Returned'), ('ACCEPTED', 'Accepted'), ('RELEASED', 'Released'), ('EXPIRED', 'Expired')], max_length=50),
        ),
        migrations.AlterField(
            model_name='remarks',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
