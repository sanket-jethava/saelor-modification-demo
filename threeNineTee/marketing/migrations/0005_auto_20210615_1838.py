# Generated by Django 3.1.2 on 2021-06-15 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0004_auto_20210615_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotion_banner',
            name='from_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='promotion_banner',
            name='to_date',
            field=models.DateField(),
        ),
    ]
