# Generated by Django 3.1.2 on 2021-06-09 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0074_package_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='b2bSubUserRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parentb2b_user_id', models.BigIntegerField()),
                ('subb2b_user_id', models.BigIntegerField()),
            ],
        ),
    ]
