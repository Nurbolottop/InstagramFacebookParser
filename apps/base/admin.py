from django.contrib import admin
from django.contrib.auth.models import User,Group
################################################################################################################################################################################
from .models import InstagramProfile, InstagramPost

class InstagramProfileFilterAdmin(admin.ModelAdmin):
    list_display = ('username',)
    search_fields = ('username',)
    readonly_fields = ('username',)


class InstagramPostFilterAdmin(admin.ModelAdmin):
    list_display = ('profile','description','created_at')
    search_fields = ('profile','description','created_at')
    readonly_fields = ('profile','description','created_at',)
      
admin.site.register(InstagramProfile,InstagramProfileFilterAdmin)
admin.site.register(InstagramPost,InstagramPostFilterAdmin)


################################################################################################################################################################################

admin.site.unregister(User)
admin.site.unregister(Group)