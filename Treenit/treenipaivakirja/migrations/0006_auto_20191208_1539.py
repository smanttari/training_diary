# Generated by Django 2.2.4 on 2019-12-08 13:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('treenipaivakirja', '0005_auto_20191123_1608'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='kausi',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='laji',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='tehoalue',
            unique_together=set(),
        ),
    ]