from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from apps.contacts.models import InstagramProfile
import instaloader
import requests

@shared_task
def add_instagram_profile_and_posts(profile_id):
    profile = InstagramProfile.objects.get(id=profile_id)
    profile._parse_instagram_data()