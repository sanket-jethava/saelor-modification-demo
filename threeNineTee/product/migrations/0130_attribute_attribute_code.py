# Generated by Django 3.1.2 on 2021-06-21 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0129_add_product_types_and_attributes_perm'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='attribute_code',
            field=models.CharField(default=None, max_length=50),
        ),
    ]
