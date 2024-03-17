from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib import messages
from urllib.parse import urlparse, unquote
from django.core.exceptions import SuspiciousFileOperation
import instaloader, requests, os, hashlib

from apps.contacts.tasks import add_instagram_profile_and_posts


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
        blank=True, null=True,
        max_length=500  # Увеличиваем максимальную длину
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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        try:
            # Предполагается, что some_task_that_uses_instaloader - это ваша задача Celery,
            # которая выполняет вход в Instaloader
            add_instagram_profile_and_posts.delay(obj.id)
        except instaloader.exceptions.ConnectionException as e:
            # Сюда мы попадаем, если было поймано исключение при выполнении задачи
            messages.error(request, f"Произошла ошибка при входе: {e}")

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

    def _save_profile_image(self, profile_pic_url):
        """
        Сохранение изображения профиля с уникальным именем файла
        """
        response = requests.get(profile_pic_url)
        if response.status_code == 200:
            # Разбираем URL на части и извлекаем путь
            path = urlparse(unquote(profile_pic_url)).path
            # Извлекаем расширение файла
            file_extension = os.path.splitext(path)[1].lower()
            # Ограничиваем расширение до 4 символов (если это необычное расширение, возможно потребуется другой подход)
            file_extension = file_extension[:5] if file_extension.startswith('.j') else file_extension[:4]
            # Генерируем имя файла на основе хэша URL
            file_name = hashlib.sha256(profile_pic_url.encode('utf-8')).hexdigest()[:12]
            full_file_name = f"{file_name}{file_extension}"
            self.profile_image.save(full_file_name, ContentFile(response.content), save=False)

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
        self.instagram_id = str(profile.userid)  # Преобразуем ID в строку, если он числовой
        self.count_followers = profile.followers
        self.count_posts = profile.mediacount
        self.save()

        # Downloading the profile picture
        # Предполагается, что профиль загружен
        new_profile_pic_url = profile.profile_pic_url
        if new_profile_pic_url and (not self.profile_image or self._profile_image_changed(new_profile_pic_url)):
            try:
                self._save_profile_image(new_profile_pic_url)
            except SuspiciousFileOperation:
                # Если имя файла слишком длинное, логируем ошибку или принимаем меры
                print("Ошибка при сохранении изображения: имя файла слишком длинное.")
                
        # Сохранить изменения в профиле
        self.save(update_fields=['profile_image', 'count_followers', 'count_posts', 'instagram_id'])

        # Parsing and saving/updating the last 10 posts
        for post in profile.get_posts():
            post_obj, created = InstagramPost.objects.update_or_create(
                instagram_id=str(post.mediaid),  # Убедитесь, что instagram_id — это строка
                defaults={
                    'profile': self,
                    'post_url': f"https://www.instagram.com/p/{post.shortcode}/",
                    'image_url': post.url,
                    'description': post.caption if post.caption else "Описание отсутствует",
                    'created_instagram': post.date_utc,
                    'count_likes': post.likes,
                    'count_views': post.video_view_count or 0,
                    'created_at': timezone.now(),
                }
            )

            # Получаем и сохраняем/обновляем комментарии к каждому посту
            for comment in post.get_comments():
                InstagramComment.objects.update_or_create(
                    instagram_id=str(comment.id),  # Убедитесь, что instagram_id — это строка
                    defaults={
                        'post': post_obj,
                        'text': comment.text,
                        'username': comment.owner.username,
                        'profile_url': f"https://www.instagram.com/{comment.owner.username}/",
                        'created_instagram': comment.created_at_utc,
                        'created_at': timezone.now(),
                    }
                )

            if len(InstagramPost.objects.filter(profile=self)) >= 10:
                break  # Прекращаем обработку после получения и обработки 10 постов

    def delete(self, *args, **kwargs):
        # Если у объекта есть изображение, удаляем его
        if self.profile_image:
            if os.path.isfile(self.profile_image.path):
                os.remove(self.profile_image.path)
        super(InstagramProfile, self).delete(*args, **kwargs)

    def _profile_image_changed(self, new_profile_pic_url):
        """Проверка, изменилась ли фотография профиля."""
        # Проверка по URL фотографии
        if self.profile_image and new_profile_pic_url:
            response = requests.get(new_profile_pic_url, stream=True)
            if response.status_code == 200:
                # Сравнение хэшей изображений
                hash_new_image = hashlib.sha256(response.content).hexdigest()
                self.profile_image.open()
                hash_current_image = hashlib.sha256(self.profile_image.read()).hexdigest()
                self.profile_image.close()
                return hash_new_image != hash_current_image
        return True

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

class CeleryTaskErrorLog(models.Model):
    task_name = models.CharField(
        max_length=255, verbose_name="Название задачи celery"
    )
    error_message = models.TextField(
        verbose_name="Сообщение ошибки"
    )
    timestamp = models.DateTimeField(
        verbose_name="Дата ошибки",auto_now_add=True
    )
    
    class Meta:
        verbose_name = 'Celery Логи'
        verbose_name_plural = 'Celery Логи'