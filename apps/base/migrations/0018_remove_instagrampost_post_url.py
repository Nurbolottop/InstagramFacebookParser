# Generated by Django 5.0.2 on 2024-03-01 03:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_instagrampost_post_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instagrampost',
            name='post_url',
        ),
    ]