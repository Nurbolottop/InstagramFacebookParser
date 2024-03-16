from celery import shared_task
from apps.contacts.models import InstagramProfile

@shared_task
def add_instagram_profile_and_posts(profile_id):
    profile = InstagramProfile.objects.get(id=profile_id)
    profile._parse_instagram_data()

@shared_task
def update_instagram_data():
    for profile in InstagramProfile.objects.all():
        profile._parse_instagram_data()  # Вызов вашего метода обновления данных