# Generated by Django 3.1.2 on 2021-06-18 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_management', '0008_jobapplications_is_accept'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobapplications',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]