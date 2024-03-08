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
        creating = self._state.adding
        super().save(*args, **kwargs)  # Сначала сохраняем профиль
        if creating:  # Если это создание нового профиля
            from apps.contacts.tasks import add_instagram_profile_and_posts  # Импорт перенесён сюда
            add_instagram_profile_and_posts.delay(self.id)  # Вызов задачи в асинхронном режиме

    def _parse_instagram_data(self):
        self.username = self.url.split("/")[-2]  # Extracting the username from URL

        # Initialize Instaloader with authentication
        L = instaloader.Instaloader()

        # Providing login credentials for Instagram authentication
        if settings.INSTAGRAM_USERNAME and settings.INSTAGRAM_PASSWORD:
            L.context.login(settings.INSTAGRAM_USERNAME, settings.INSTAGRAM_PASSWORD)
        
        # Loading the profile
        profile = instaloader.Profile.from_username(L.context, self.username)

        # Saving the profile
        super().save()

        # Parsing and saving the last 10 posts
        posts_to_create = []
        for post in profile.get_posts():
            if len(posts_to_create) >= 10:
                break

            # Check for the presence of a description before creating the InstagramPost object
            # If post.caption is None or an empty string, set description to "Описание отсутствует"
            description = post.caption if post.caption else "Описание отсутствует"
            post_obj = InstagramPost(
                profile=self,
                post_url=f"https://www.instagram.com/p/{post.shortcode}/",
                image_url=post.url,
                description=description,
                created_at=post.date,
            )
            post_obj.save()  # Saving each post separately

            # Getting and saving comments for each post
            comments = [(comment.text, comment.owner.username) for comment in post.get_comments()]
            for comment_text, username in comments:
                profile_url = f"https://www.instagram.com/{username}/"  # Generating the user profile URL
                InstagramComment.objects.create(post=post_obj, text=comment_text, username=username, profile_url=profile_url)


    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

class InstagramPost(models.Model):
    profile = models.ForeignKey(
        InstagramProfile, on_delete=models.CASCADE,
        related_name="profile_posts",
        verbose_name="Профиль"
    )
    post_url = models.URLField(
        verbose_name="Ссылка на пост"
    )
    image_url = models.URLField(
        verbose_name="Ссылка на изображение",
        blank=True, null=True
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True, default="Описание отсутствует"
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.description
    
    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

class InstagramComment(models.Model):
    post = models.ForeignKey(
        InstagramPost, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Пост"
    )
    text = models.TextField(
        verbose_name="Текст"
    )
    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=255, blank=True
    )  # Имя пользователя Instagram, оставившего комментарий
    profile_url = models.URLField(
        verbose_name="Ссылка на профиль",
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.post} {self.text}"
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"