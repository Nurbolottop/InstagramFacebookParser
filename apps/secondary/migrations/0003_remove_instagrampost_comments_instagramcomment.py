# Generated by Django 5.0.2 on 2024-02-29 22:27

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secondary', '0002_alter_instagrampost_comments_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instagrampost',
            name='comments',
        ),
        migrations.CreateModel(
            name='InstagramComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='secondary.instagrampost')),
            ],
        ),
    ]
