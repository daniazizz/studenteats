# Generated by Django 3.0 on 2019-12-16 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_post_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='cost',
            field=models.IntegerField(default=0),
        ),
    ]