# Generated by Django 2.2.4 on 2019-11-23 13:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('treenipaivakirja', '0002_auto_20191123_1454'),
    ]

    operations = [
        migrations.CreateModel(
            name='kausi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kausi', models.CharField(max_length=20)),
                ('alkupvm', models.DateField(verbose_name='Alkupäivä')),
                ('loppupvm', models.DateField(verbose_name='Loppupäivä')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Kausi',
                'unique_together': {('kausi', 'user')},
            },
        ),
    ]
