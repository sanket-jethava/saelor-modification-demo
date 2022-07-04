# Generated by Django 3.1.2 on 2021-05-05 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0047_auto_20200810_1415'),
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('price', models.BigIntegerField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='available_token',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.TextField(default=None, max_length=6),
        ),
        migrations.AddField(
            model_name='user',
            name='gst_number',
            field=models.TextField(blank=True, default=None, max_length=15),
        ),
        migrations.AddField(
            model_name='user',
            name='is_artist',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_loginwith_facebook',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_loginwith_google',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='package_id',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='pan_number',
            field=models.TextField(blank=True, default=None, max_length=10),
        ),
        migrations.AddField(
            model_name='user',
            name='phonenumber',
            field=models.TextField(blank=True, default=None, max_length=10),
        ),
    ]
