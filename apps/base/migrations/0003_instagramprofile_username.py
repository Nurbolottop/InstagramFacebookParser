# Generated by Django 5.0.2 on 2024-02-27 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_remove_instagramprofile_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='instagramprofile',
            name='username',
            field=models.CharField(default=1, max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
