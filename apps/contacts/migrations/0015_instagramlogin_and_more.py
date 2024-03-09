# Generated by Django 5.0.2 on 2024-03-09 16:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0014_instagramcomment_created_instagram_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramLogin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=255, verbose_name='Логин')),
                ('password', models.CharField(max_length=255, verbose_name='Пароль')),
            ],
            options={
                'verbose_name': 'Логины для входов',
            },
        ),
        migrations.AlterField(
            model_name='instagramcomment',
            name='created_instagram',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата создания комментария'),
        ),
        migrations.AddField(
            model_name='instagramprofile',
            name='authorization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authorization_profile', to='contacts.instagramlogin', verbose_name='Авторазация аккаунта'),
        ),
    ]
