# Generated by Django 3.1.2 on 2021-05-14 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0064_auto_20210514_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
