# Generated by Django 4.1.7 on 2023-08-20 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_gender'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permittee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('farm_name', models.CharField(max_length=255)),
                ('farm_address', models.TextField()),
                ('permittee_photo', models.ImageField(upload_to='uploaded-media/')),
                ('farm_photo', models.ImageField(upload_to='uploaded-media/')),
            ],
        ),
    ]
