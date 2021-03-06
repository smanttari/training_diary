# Generated by Django 2.2.10 on 2020-08-22 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('treenipaivakirja', '0004_polarsport'),
    ]

    operations = [
        migrations.CreateModel(
            name='PolarSleep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('duration', models.DecimalField(decimal_places=2, max_digits=4)),
                ('continuity', models.DecimalField(decimal_places=1, max_digits=2)),
                ('light_sleep', models.DecimalField(decimal_places=2, max_digits=4)),
                ('deep_sleep', models.DecimalField(decimal_places=2, max_digits=4)),
                ('rem_sleep', models.DecimalField(decimal_places=2, max_digits=4)),
                ('sleep_score', models.IntegerField()),
                ('total_interruption_duration', models.DecimalField(decimal_places=2, max_digits=4)),
                ('polar_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='treenipaivakirja.PolarUser')),
            ],
            options={
                'unique_together': {('polar_user', 'date')},
            },
        ),
        migrations.CreateModel(
            name='PolarRecharge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('heart_rate_avg', models.IntegerField()),
                ('heart_rate_variability_avg', models.IntegerField()),
                ('nightly_recharge_status', models.IntegerField()),
                ('polar_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='treenipaivakirja.PolarUser')),
            ],
            options={
                'unique_together': {('polar_user', 'date')},
            },
        ),
    ]
