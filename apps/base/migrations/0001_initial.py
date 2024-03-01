# Generated by Django 5.0.2 on 2024-03-01 19:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=255, unique=True)),
                ('url', models.URLField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='InstagramPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField(verbose_name='Фотография')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('created_at', models.DateTimeField(verbose_name='Дата создания')),
                ('post_url', models.URLField(blank=True, null=True, verbose_name='Ссылка на публикацию')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.instagramprofile', verbose_name='Профиль')),
            ],
            options={
                'verbose_name': 'Публикация',
                'verbose_name_plural': 'Публикации',
                'ordering': ['-created_at'],
            },
        ),
    ]
