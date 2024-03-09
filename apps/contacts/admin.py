from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.db import models
from django.template.defaultfilters import truncatechars
from apps.contacts.models import InstagramLogin, InstagramProfile, InstagramPost, InstagramComment

class InstagramPostTabularInline(admin.TabularInline):
    model = InstagramPost
    extra = 0

class InstagramCommentTabularInline(admin.TabularInline):
    model = InstagramComment
    extra = 0

# @admin.register(InstagramLogin)
class InstagramLoginAdmin(admin.ModelAdmin):
    list_display = ('login', 'password')
    search_fields = ('login', 'password')

class InstagramProfileFilterAdmin(admin.ModelAdmin):
    list_display = ('username_with_icon', 'get_post_count', 'get_comment_count', 'created')  # Добавляем новое поле get_comment_count в list_display
    search_fields = ('username',)
    readonly_fields = ('username', 'profile_image')
    inlines = (InstagramPostTabularInline, )

    def username_with_icon(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width: 25px; height: 25px; margin-right: 5px; border-radius: 50%;" />{}', obj.profile_image.url, obj.username)
        else:
            return obj.username

    username_with_icon.short_description = 'Username'

    def get_post_count(self, obj):
        return obj.profile_posts.count() or 0  # Считаем количество связанных постов с профилем

    get_post_count.short_description = 'Количество постов'  # Описание для колонки

    def get_comment_count(self, obj):
        return obj.profile_posts.annotate(comment_count=models.Count('comments')).aggregate(total_comments=models.Sum('comment_count'))['total_comments'] or 0

    get_comment_count.short_description = 'Колличество комментариев'

class InstagramCommentAdmin(admin.ModelAdmin):
    list_filter = ('post__profile__username', )
    # list_display = ('username_with_icon', 'text', 'profile_url_link')
    list_display = ('short_post', 'get_post_url', 'username', 'text', 'profile_url_link', 'created_instagram')
    search_fields = ('username', 'text', 'profile_url')

    # def username_with_icon(self, obj):
    #     icon_path = settings.STATIC_URL + 'images/profilejpg'  # Путь к изображению
    #     return format_html('<img src="{}" style="width: 25px; height: 25px; margin-right: 5px; border-radius: 50%;" />{}', icon_path, obj.username)

    # username_with_icon.short_description = 'Username'

    def short_post(self, obj):
        """
        Метод для отображения сокращенного текста поста до 10 символов.
        """
        return truncatechars(obj.post.description, 15)  # Обрезаем текст до 10 символов

    def get_post_url(self, obj):
        """
        Метод для отображения URL связанного поста.
        """
        # return obj.post.post_url
        return format_html('<a href="{}" target="_blank">{}</a>', obj.post.post_url, obj.post.post_url)

    def profile_url_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.profile_url, obj.profile_url)

    profile_url_link.short_description = 'Ссылка на профиль'
    short_post.short_description = "Пост"
    get_post_url.short_description = "Ссылка на пост"

class InstagramPostFilterAdmin(admin.ModelAdmin):
    list_display = ('profile', 'description', 'created_instagram')
    list_filter = ('profile', )
    search_fields = ('profile', 'description', 'created_instagram', 'created_at')
    readonly_fields = ('profile', 'description', 'created_instagram', 'created_at',)
    inlines = (InstagramCommentTabularInline, )

# admin.site.register(InstagramProfile, InstagramProfileFilterAdmin)
# admin.site.register(InstagramComment, InstagramCommentAdmin)
# admin.site.register(InstagramPost, InstagramPostFilterAdmin)
admin.site.register(InstagramLogin, InstagramLoginAdmin)
admin.site.register(InstagramProfile, InstagramProfileFilterAdmin)
admin.site.register(InstagramPost, InstagramPostFilterAdmin)
admin.site.register(InstagramComment, InstagramCommentAdmin)
