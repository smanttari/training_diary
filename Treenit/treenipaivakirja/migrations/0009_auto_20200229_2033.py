# Generated by Django 2.2.10 on 2020-02-29 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('treenipaivakirja', '0008_auto_20200222_2212'),
    ]

    operations = [
        migrations.AddField(
            model_name='harjoitus',
            name='vauhti_min',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='min'),
        ),
        migrations.AddField(
            model_name='harjoitus',
            name='vauhti_s',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='s'),
        ),
        migrations.AlterField(
            model_name='harjoitus',
            name='aika',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='treenipaivakirja.Aika', verbose_name='vvvvkkpp'),
        ),
        migrations.AlterField(
            model_name='harjoitus',
            name='laji',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='treenipaivakirja.Laji', verbose_name='Laji'),
        ),
        migrations.AlterField(
            model_name='teho',
            name='harjoitus',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='treenipaivakirja.Harjoitus'),
        ),
        migrations.AlterField(
            model_name='teho',
            name='tehoalue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='treenipaivakirja.Tehoalue'),
        ),
    ]
