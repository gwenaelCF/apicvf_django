# Generated by Django 2.2.9 on 2020-01-29 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apicvf', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dept',
            name='insee',
            field=models.CharField(max_length=6, unique=True),
        ),
        migrations.AlterField(
            model_name='grain',
            name='insee',
            field=models.CharField(max_length=6, unique=True),
        ),
        migrations.AlterField(
            model_name='region',
            name='insee',
            field=models.CharField(max_length=6, unique=True),
        ),
    ]