# Generated by Django 3.1.2 on 2021-05-11 10:27

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0056_auto_20210511_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginsummary',
            name='date',
            field=models.DateField(blank=True, default=datetime.date.today, null=True),
        ),
        migrations.AlterField(
            model_name='loginsummary',
            name='device_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='loginsummary',
            name='login_time',
            field=models.TimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='loginsummary',
            name='logout_time',
            field=models.TimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True),
        ),
    ]