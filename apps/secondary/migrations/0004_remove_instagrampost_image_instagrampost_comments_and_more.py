# Generated by Django 5.0.2 on 2024-02-29 22:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secondary', '0003_remove_instagrampost_comments_instagramcomment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instagrampost',
            name='image',
        ),
        migrations.AddField(
            model_name='instagrampost',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='instagrampost',
            name='image_url',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='instagrampost',
            name='post_url',
            field=models.URLField(validators=[django.core.validators.URLValidator()]),
        ),
        migrations.DeleteModel(
            name='InstagramComment',
        ),
    ]
