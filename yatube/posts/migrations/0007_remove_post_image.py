# Generated by Django 2.2.6 on 2021-07-18 00:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_post_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
    ]