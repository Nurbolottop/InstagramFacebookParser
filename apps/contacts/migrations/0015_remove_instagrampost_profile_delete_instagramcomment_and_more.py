# Generated by Django 5.0.2 on 2024-03-01 03:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0014_alter_instagrampost_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instagrampost',
            name='profile',
        ),
        migrations.DeleteModel(
            name='InstagramComment',
        ),
        migrations.DeleteModel(
            name='InstagramPost',
        ),
        migrations.DeleteModel(
            name='InstagramProfile',
        ),
    ]