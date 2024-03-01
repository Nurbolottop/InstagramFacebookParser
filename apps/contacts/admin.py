from django.contrib import admin
from django.contrib.auth.models import User,Group
################################################################################################################################################################################
from .models import InstagramProfile, InstagramPost,InstagramComment

class InstagramProfileFilterAdmin(admin.ModelAdmin):
    list_filter = ('username', )
    list_display = ('username',)
    search_fields = ('username',)
    readonly_fields = ('username',)

class InstagramCommentFilterAdmin(admin.ModelAdmin):
    list_filter = ('post','text', )
    list_display = ('post','text',)
    search_fields = ('post','text',)
    readonly_fields = ('post','text',)

class InstagramPostFilterAdmin(admin.ModelAdmin):
    list_filter = ('profile','description','created_at' )
    list_display = ('profile','description','created_at')
    search_fields = ('profile','description','created_at')
    readonly_fields = ('profile','description','created_at',)
    
admin.site.register(InstagramComment,InstagramCommentFilterAdmin)
admin.site.register(InstagramProfile,InstagramProfileFilterAdmin)
admin.site.register(InstagramPost,InstagramPostFilterAdmin)


################################################################################################################################################################################
