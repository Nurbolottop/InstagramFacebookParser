from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage

from apps.contacts.models import InstagramProfile

@receiver(post_delete, sender=InstagramProfile)
def delete_profile_image(sender, instance, **kwargs):
    print("SIGNAL")
    print(instance.profile_image)
    if instance.profile_image:
        # Удаляем файл изображения, если он существует
        print(default_storage.exists(instance.profile_image.name))
        if default_storage.exists(instance.profile_image.name):
            print("DELETE")
            default_storage.delete(instance.profile_image.name)
