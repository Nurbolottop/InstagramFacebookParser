from django.db import models
from django.utils import timezone
import instaloader

class InstagramSettings(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class InstagramPost(models.Model):
    post_url = models.URLField()
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        if not self.pk:  # Если объект сохраняется впервые
            settings = InstagramSettings.objects.first()  # Получаем первую запись из модели InstagramSettings
            if settings:
                loader = instaloader.Instaloader()
                loader.login(settings.username, settings.password)
                post = instaloader.Post.from_shortcode(loader.context, self.post_url.split('/')[-2])
                if not self.description:
                    self.description = post.caption
                if not self.created_at:
                    self.created_at = post.date_utc
                if not self.image_url:
                    self.image_url = post.url
            
                super().save(*args, **kwargs)  # Сначала сохраняем объект, чтобы у него был доступ к первичному ключу
                comments = [(comment.text, comment.owner.username) for comment in post.get_comments()]  # Используем owner.username для получения имени пользователя
                for comment_text, username in comments:
                    profile_url = f"https://www.instagram.com/{username}/"  # Генерируем URL профиля пользователя
                    InstagramComment.objects.create(post=self, text=comment_text, username=username, profile_url=profile_url)
            else:
                super().save(*args, **kwargs)  # Сохраняем объект, но не заполняем поля комментариев, так как у нас нет настроек
        else:
            super().save(*args, **kwargs)

class InstagramComment(models.Model):
    post = models.ForeignKey(InstagramPost, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    username = models.CharField(max_length=100)  # Имя пользователя, оставившего комментарий
    profile_url = models.URLField()  # Ссылка на профиль пользователя
    created_at = models.DateTimeField(default=timezone.now)
