# Generated by Django 3.1.2 on 2021-06-16 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Jobs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.TextField(null=True, unique=True)),
                ('required_experience', models.TextField(blank=True)),
                ('job_description', models.TextField(blank=True)),
                ('post_date', models.DateField()),
                ('status', models.BooleanField(default=False)),
            ],
        ),
    ]
