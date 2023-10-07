# Generated by Django 4.1.7 on 2023-10-07 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0056_signature_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='transportentry',
            name='description',
            field=models.CharField(default='pupae', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='localtransportpermit',
            name='wcp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wcp_ltps', to='permits.wildlifecollectorpermit', verbose_name="Wildlife Collector's Permit"),
        ),
        migrations.AlterField(
            model_name='localtransportpermit',
            name='wfp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wfp_ltps', to='permits.wildlifefarmpermit', verbose_name='Wildlife Farm Permit'),
        ),
    ]
