# Generated by Django 3.0 on 2019-12-11 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20191211_2054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='_profile_following_+', to='users.Profile'),
        ),
    ]
