# Generated by Django 3.0 on 2019-12-11 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20191211_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(default='', max_length=100),
        ),
    ]
