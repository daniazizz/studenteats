# Generated by Django 3.0 on 2019-12-11 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_profile_following'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='following',
            field=models.ManyToManyField(related_name='_profile_following_+', to='users.Profile'),
        ),
    ]
