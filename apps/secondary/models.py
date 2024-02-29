from django.db import models
from django.utils import timezone
import instaloader

class InstagramPost(models.Model):
    post_url = models.URLField()
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    comments = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Если объект сохраняется впервые
            loader = instaloader.Instaloader()
            loader.login("shus_dv", "erk1nbaew")  # Новые имя пользователя и пароль
            post = instaloader.Post.from_shortcode(loader.context, self.post_url.split('/')[-2])
            if not self.description:
                self.description = post.caption
            if not self.created_at:
                self.created_at = post.date_utc
            if not self.comments:
                self.comments = '\n'.join([comment.text for comment in post.get_comments()])
            if not self.image_url:
                self.image_url = post.url
        super().save(*args, **kwargs)
