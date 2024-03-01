# Generated by Django 5.0.2 on 2024-03-01 03:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0013_alter_instagramcomment_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='instagrampost',
            options={'ordering': ['-created_at'], 'verbose_name': 'Публикация', 'verbose_name_plural': 'Публикации'},
        ),
        migrations.RemoveField(
            model_name='instagramcomment',
            name='post_url',
        ),
        migrations.AddField(
            model_name='instagramcomment',
            name='post',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='contacts.instagrampost'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='instagramcomment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='instagramcomment',
            name='text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='instagrampost',
            name='created_at',
            field=models.DateTimeField(verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='instagrampost',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='instagrampost',
            name='image_url',
            field=models.URLField(default=1, verbose_name='Фотография'),
            preserve_default=False,
        ),
    ]
