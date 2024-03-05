from django.db import models
import instaloader

class InstagramProfile(models.Model):
    username = models.CharField(max_length=255, unique=True, blank=True)
    url = models.URLField(unique=True)

    def save(self, *args, **kwargs):
        if not self.username:  # Если username не установлен
            self._parse_instagram_data()
        super().save(*args, **kwargs)

    def _parse_instagram_data(self):
        self.username = self.url.split("/")[-2]  # Извлечение имени пользователя из URL

        # Инициализация Instaloader с аутентификацией
        L = instaloader.Instaloader()
        
        # Указание логина и пароля для аутентификации в Instagram
        L.context.login('nikakika76', 'kuma2711')
        
        # Загрузка профиля
        profile = instaloader.Profile.from_username(L.context, self.username)

        # Сохранение профиля
        self.save()

        # Парсинг и сохранение последних 10 постов
        # Парсинг и сохранение последних 10 постов
        posts_to_create = []
        for post in profile.get_posts():
            if len(posts_to_create) >= 10:
                break
            posts_to_create.append(InstagramPost(
                profile=self,
                image_url=post.url,
                description=post.caption,
                created_at=post.date.isoformat(),
                post_url=f"https://www.instagram.com/p/{post.shortcode}/"  # Сохраняем ссылку на публикацию
            ))
        InstagramPost.objects.bulk_create(posts_to_create)

class InstagramPost(models.Model):
    profile = models.ForeignKey(InstagramProfile, 
            on_delete=models.CASCADE,
            verbose_name = "Профиль"
    )
    image_url = models.URLField(
        verbose_name = "Фотография"
    )
    description = models.TextField(
        verbose_name = "Описание",
        blank = True, null = True
    )
    created_at = models.DateTimeField(
        verbose_name = "Дата создания",
    )
    post_url = models.URLField(
        verbose_name="Ссылка на публикацию",
        blank=True, null=True
    )
    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ['-created_at']