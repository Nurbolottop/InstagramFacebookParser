from django.db import models
from django.utils import timezone
import instaloader
from django.core.files.base import ContentFile
from urllib.request import urlopen

class InstagramPost(models.Model):
    post_url = models.URLField()
    image = models.ImageField(upload_to='instagram_posts', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    comments = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Если объект сохраняется впервые
            loader = instaloader.Instaloader()
            loader.login("deviates.kg", "erk1nbaew")  # Ваше имя пользователя и пароль
            post = instaloader.Post.from_shortcode(loader.context, self.post_url.split('/')[-2])
            if not self.description:
                self.description = post.caption
            if not self.created_at:
                self.created_at = post.date_utc
            if not self.comments:
                self.comments = '\n'.join([comment.text for comment in post.get_comments()])
            if not self.image:
                image_data = urlopen(post.url).read()
                self.image.save(f'{self.pk}.jpg', ContentFile(image_data))
        super().save(*args, **kwargs)
