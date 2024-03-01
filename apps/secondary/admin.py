# admin.py
from django.contrib import admin
from .models import InstagramPost,InstagramComment

admin.site.register(InstagramPost)
admin.site.register(InstagramComment)

