# Generated by Django 2.2.7 on 2019-11-20 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_postimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
    ]
