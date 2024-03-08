from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.db import models
from .models import InstagramProfile, InstagramPost, InstagramComment

class InstagramProfileFilterAdmin(admin.ModelAdmin):
    list_display = ('username_with_icon', 'get_comment_count')  # Добавляем новое поле get_comment_count в list_display
    search_fields = ('username',)
    readonly_fields = ('username',)

    def username_with_icon(self, obj):
        icon_path = settings.STATIC_URL + 'images/profilejpg'  # Путь к изображению
        return format_html('<img src="{}" style="width: 25px; height: 25px; margin-right: 5px; border-radius: 50%;" />{}', icon_path, obj.username)

    username_with_icon.short_description = 'Username'

    def get_comment_count(self, obj):
        return obj.profile_posts.annotate(comment_count=models.Count('comments')).aggregate(total_comments=models.Sum('comment_count'))['total_comments']

    get_comment_count.short_description = 'Колличество комментариев'

class InstagramCommentAdmin(admin.ModelAdmin):
    list_display = ('username_with_icon', 'text', 'profile_url_link')
    search_fields = ('username', 'text', 'profile_url')

    def username_with_icon(self, obj):
        icon_path = settings.STATIC_URL + 'images/profilejpg'  # Путь к изображению
        return format_html('<img src="{}" style="width: 25px; height: 25px; margin-right: 5px; border-radius: 50%;" />{}', icon_path, obj.username)

    username_with_icon.short_description = 'Username'

    def profile_url_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.profile_url, obj.profile_url)

    profile_url_link.short_description = 'Profile URL'

class InstagramPostFilterAdmin(admin.ModelAdmin):
    list_display = ('profile', 'description', 'created_at')
    list_filter = ('profile', )
    search_fields = ('profile', 'description', 'created_at')
    readonly_fields = ('profile', 'description', 'created_at',)

admin.site.register(InstagramComment, InstagramCommentAdmin)
admin.site.register(InstagramProfile, InstagramProfileFilterAdmin)
admin.site.register(InstagramPost, InstagramPostFilterAdmin)
