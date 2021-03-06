# Generated by Django 3.1.2 on 2021-06-15 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner_image', models.TextField(null=True)),
                ('title', models.TextField(null=True)),
                ('sub_title', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('status', models.BooleanField(default=False)),
            ],
        ),
    ]
