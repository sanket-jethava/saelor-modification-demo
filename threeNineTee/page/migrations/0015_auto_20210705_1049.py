# Generated by Django 3.1.2 on 2021-07-05 05:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0014_add_metadata'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ('slug',)},
        ),
    ]