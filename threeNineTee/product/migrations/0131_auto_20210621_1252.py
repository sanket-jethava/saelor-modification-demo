# Generated by Django 3.1.2 on 2021-06-21 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0130_attribute_attribute_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='attribute_code',
            field=models.CharField(blank=True, default=None, max_length=50),
        ),
    ]
