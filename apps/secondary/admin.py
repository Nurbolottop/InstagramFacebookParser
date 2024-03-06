from django.contrib import admin
from django.utils.html import format_html
from .models import InstagramPost, InstagramComment, InstagramSettings

class InstagramCommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'text', 'profile_url_link')
    search_fields = ('username', 'text', 'profile_url')

    def profile_url_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.profile_url, obj.profile_url)

    profile_url_link.short_description = 'Profile URL'

class InstagramSettingsAdmin(admin.ModelAdmin):
    list_display = ('username', 'password')

admin.site.register(InstagramPost)
admin.site.register(InstagramComment, InstagramCommentAdmin)
admin.site.register(InstagramSettings, InstagramSettingsAdmin)
