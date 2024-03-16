from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from urllib.parse import urlparse, parse_qs
import instaloader, requests, os


class InstagramLogin(models.Model):
    login = models.CharField(
        max_length=255, verbose_name="Логин"
    )
    password = models.CharField(
        max_length=255, verbose_name="Пароль"
    )

    def __str__(self):
        return f"Аккаунт {self.login}"
    
    class Meta:
        verbose_name = "Логин для входа"
        verbose_name_plural = "Логины для входов"

class InstagramProfile(models.Model):
    authorization = models.ForeignKey(
        InstagramLogin, on_delete=models.SET_NULL,
        related_name="authorization_profile",
        verbose_name="Авторазация аккаунта",
        null=True
    )
    instagram_id = models.CharField(max_length=255, verbose_name="Instagram ID", blank=True, null=True)
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
    profile_image = models.ImageField(
        verbose_name="Фотография профиля",
        upload_to='profile_images/',
        blank=True, null=True
    )
    count_followers = models.IntegerField(
        verbose_name="Количество подписчиков",
        default=0, blank=True, null=True
    )
    count_posts = models.IntegerField(
        verbose_name="Количество постов",
        default=0, blank=True, null=True
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        creating = self._state.adding
        if creating:
            # Извлекаем username из URL
            self.username = self.clean_url()

            # Если username не получен, выходим из функции сохранения
            if not self.username:
                raise ValueError('Не удалось извлечь username из предоставленного URL.')

        super().save(*args, **kwargs)

        # Только если это новый объект, запускаем асинхронное обновление данных
        if creating:
            from apps.contacts.tasks import add_instagram_profile_and_posts
            add_instagram_profile_and_posts.delay(self.id)

    def clean_url(self):
        """
        Преобразует URL в стандартный формат и извлекает username.
        """
        parsed_url = urlparse(self.url)

        # Очищаем параметры запроса и фрагменты URL, если они есть
        url_cleaned = parsed_url._replace(query="", fragment="").geturl()

        # Проверяем, содержит ли путь имя пользователя Instagram
        if parsed_url.netloc == 'www.instagram.com' and parsed_url.path:
            path_segments = parsed_url.path.strip("/").split('/')
            # Берем только первый сегмент пути как потенциальное имя пользователя
            return path_segments[0] if path_segments else ''
        return ''

    def _parse_instagram_data(self):
        self.username = self.url.split("/")[-2]  # Extracting the username from URL

        # Initialize Instaloader with authentication
        L = instaloader.Instaloader()

        # Providing login credentials for Instagram authentication
        if self.authorization.login and self.authorization.password:
            L.context.login(self.authorization.login, self.authorization.password)
        
        # Loading the profile
        profile = instaloader.Profile.from_username(L.context, self.username)
        # Обновляем информацию о профиле
        self.instagram_id = profile.userid
        self.count_followers = profile.followers
        self.count_posts = profile.mediacount
        self.save()

        # Downloading the profile picture
        if profile.profile_pic_url:
            response = requests.get(profile.profile_pic_url)
            if response.status_code == 200:
                # Create a temporary file for the downloaded image
                img_temp = NamedTemporaryFile(delete=False)  # delete=False is important here
                img_temp.write(response.content)
                img_temp.flush()
                
                # Reopen the temporary file to read
                img_temp.seek(0)
                
                # Save the image in the model field
                self.profile_image.save(f"profile_{self.username}.jpg", ContentFile(img_temp.read()), save=True)
                
                # Now that we've saved the image in Django, we can close and delete the temp file
                img_temp.close()

        # Saving the profile
        super().save()

        # Parsing and saving the last 10 posts
        posts_to_create = []
        # Получаем только последние 10 постов
        for post in profile.get_posts():
            posts_to_create.append(post)
            if len(posts_to_create) >= 10:
                break
            
            # If post.caption is None or an empty string, set description to "Описание отсутствует"
            description = post.caption if post.caption else "Описание отсутствует"
            post_obj = InstagramPost(
                profile=self,
                instagram_id=post.mediaid,
                post_url=f"https://www.instagram.com/p/{post.shortcode}/",
                image_url=post.url,
                description=description,
                created_instagram=post.date_utc,  # Set the Instagram creation date
                count_likes=post.likes,
                count_views=post.video_view_count or 0,
                created_at=timezone.now()  # Set the current time as the add date
            )
            post_obj.save()  # Saving each post separately

            # Getting and saving comments for each post
            for comment in post.get_comments():
                InstagramComment.objects.create(
                    post=post_obj,
                    instagram_id=comment.id,
                    text=comment.text,
                    username=comment.owner.username,
                    profile_url=f"https://www.instagram.com/{comment.owner.username}/",
                    created_instagram=comment.created_at_utc,  # Set the Instagram creation date for the comment
                    created_at=timezone.now()  # Set the current time as the add date for the comment
                )

    def delete(self, *args, **kwargs):
        # Если у объекта есть изображение, удаляем его
        if self.profile_image:
            if os.path.isfile(self.profile_image.path):
                os.remove(self.profile_image.path)
        super(InstagramProfile, self).delete(*args, **kwargs)


    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

class InstagramPost(models.Model):
    profile = models.ForeignKey(
        InstagramProfile, on_delete=models.CASCADE,
        related_name="profile_posts",
        verbose_name="Профиль"
    )
    instagram_id = models.CharField(max_length=255, verbose_name="Instagram Post ID", blank=True, null=True)
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
    count_likes = models.IntegerField(
        verbose_name="Количество лайков",
        default=0, blank=True, null=True
    )
    count_views = models.IntegerField(
        verbose_name="Количество просмотров",
        default=0, blank=True, null=True
    )
    created_instagram = models.DateTimeField(
        verbose_name="Дата создания поста",
        blank=True, null=True
    )
    created_at = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True
    )

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
    instagram_id = models.CharField(max_length=255, verbose_name="Instagram Comment ID", blank=True, null=True)
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
    created_instagram = models.DateTimeField(
        verbose_name="Дата создания комментария",
        blank=True, null=True
    )
    created_at = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.post} {self.text}"
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"