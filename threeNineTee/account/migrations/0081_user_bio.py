# Generated by Django 3.1.2 on 2021-06-14 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0080_auto_20210614_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, max_length=300),
        ),
    ]
