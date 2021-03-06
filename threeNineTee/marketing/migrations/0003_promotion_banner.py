# Generated by Django 3.1.2 on 2021-06-15 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0002_auto_20210615_1407'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promotion_Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner_image', models.TextField(null=True)),
                ('title', models.TextField(null=True, unique=True)),
                ('from_date', models.DateField()),
                ('to_date', models.DateField()),
                ('status', models.BooleanField(default=False)),
            ],
        ),
    ]
