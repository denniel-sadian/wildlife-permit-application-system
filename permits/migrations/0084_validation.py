# Generated by Django 4.1.7 on 2023-10-22 11:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('permits', '0083_alter_permit_status_alter_permitapplication_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Validation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('validated_at', models.DateTimeField(auto_now_add=True)),
                ('permit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='permits.permit')),
                ('validator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]