from django.db import models
from django.utils import timezone
from django.conf import settings
import instaloader

class InstagramProfile(models.Model):
    username = models.CharField(
        max_length=255, verbose_name="Профиль Instagram",
        help_text="https://www.instagram.com/codex_kg/",
        unique=True, blank=True
    )
    url = models.URLField(
        verbose_name="Ссылка на инстаграм профиль",
        help_text="Здесь будет отображаться профиль Instagram",
        unique=True
    )

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.username:  # Если username не установлен
            self._parse_instagram_data()
        super().save(*args, **kwargs)

    def _parse_instagram_data(self):
        self.username = self.url.split("/")[-2]  # Извлечение имени пользователя из URL

        # Инициализация Instaloader с аутентификацией
        L = instaloader.Instaloader()

        # Указание логина и пароля для аутентификации в Instagram
        if settings.INSTAGRAM_USERNAME and settings.INSTAGRAM_PASSWORD:
            L.context.login(settings.INSTAGRAM_USERNAME, settings.INSTAGRAM_PASSWORD)
        
        # Загрузка профиля
        profile = instaloader.Profile.from_username(L.context, self.username)

        # Сохранение профиля
        super().save()

        # Парсинг и сохранение последних 10 постов
        posts_to_create = []
        for post in profile.get_posts():
            if len(posts_to_create) >= 10:
                break
            # Проверяем наличие описания перед созданием объекта InstagramPost
            description = post.caption if post.caption else ""
            post_obj = InstagramPost(
                profile=self,
                post_url=f"https://www.instagram.com/p/{post.shortcode}/",
                image_url=post.url,
                description=description,
                created_at=post.date,
            )
            post_obj.save()  # Сохраняем каждый пост отдельно
            # Получаем и сохраняем комментарии для каждого поста
            comments = [(comment.text, comment.owner.username) for comment in post.get_comments()]
            for comment_text, username in comments:
                profile_url = f"https://www.instagram.com/{username}/"  # Генерируем URL профиля пользователя
                InstagramComment.objects.create(post=post_obj, text=comment_text, username=username, profile_url=profile_url)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

class InstagramPost(models.Model):
    profile = models.ForeignKey(InstagramProfile, on_delete=models.CASCADE)
    post_url = models.URLField()
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)  # Поле description больше не NULL
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.description
    
    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

class InstagramComment(models.Model):
    post = models.ForeignKey(InstagramPost, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    username = models.CharField(max_length=255, blank=True)  # Имя пользователя Instagram, оставившего комментарий
    profile_url = models.URLField(blank=True)  # Ссылка на профиль пользователя, оставившего комментарий
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.post} {self.text}"
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"