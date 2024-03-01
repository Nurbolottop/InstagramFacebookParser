# admin.py
from django.contrib import admin
from .models import InstagramPost,InstagramComment

class InstagramCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'text')
    list_filter = ('post', 'text')
    search_fields = ('post', 'text')
    
admin.site.register(InstagramPost)
admin.site.register(InstagramComment,InstagramCommentAdmin)

