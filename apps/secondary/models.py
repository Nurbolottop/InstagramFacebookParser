from django.db import models
from django.utils import timezone
import instaloader

class InstagramPost(models.Model):
    post_url = models.URLField()
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.description
    def save(self, *args, **kwargs):
        if not self.pk:  # Если объект сохраняется впервые
            loader = instaloader.Instaloader()
            loader.login("parserboy_nika", "erk1nbaew")  # Новые имя пользователя и пароль
            post = instaloader.Post.from_shortcode(loader.context, self.post_url.split('/')[-2])
            if not self.description:
                self.description = post.caption
            if not self.created_at:
                self.created_at = post.date_utc
            if not self.image_url:
                self.image_url = post.url
            
            super().save(*args, **kwargs)  # Сначала сохраняем объект, чтобы у него был доступ к первичному ключу
            comments = [comment.text for comment in post.get_comments()]
            for comment_text in comments:
                InstagramComment.objects.create(post=self, text=comment_text)
        else:
            super().save(*args, **kwargs)

class InstagramComment(models.Model):
    post = models.ForeignKey(InstagramPost, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
