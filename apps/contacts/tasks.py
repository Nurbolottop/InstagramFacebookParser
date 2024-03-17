from celery import shared_task
import instaloader
from django.core.exceptions import SuspiciousOperation

@shared_task(bind=True)  # Добавление bind=True для доступа к self
def add_instagram_profile_and_posts(self, profile_id):
    from apps.contacts.models import InstagramProfile, CeleryTaskErrorLog
    try:
        profile = InstagramProfile.objects.get(id=profile_id)
        profile._parse_instagram_data()
    except instaloader.exceptions.ConnectionException as e:
        # Логируем ошибку в нашу модель. self.name теперь доступен.
        CeleryTaskErrorLog.objects.create(
            task_name=self.name,  # Теперь self.name определён благодаря bind=True
            error_message=str(e)
        )
    except SuspiciousOperation as e:
        # Обработка других типов ошибок, если они возникают
        CeleryTaskErrorLog.objects.create(
            task_name=self.name,
            error_message=f"Suspicious operation: {e}"
        )

@shared_task
def update_instagram_data():
    from apps.contacts.models import InstagramProfile, CeleryTaskErrorLog
    for profile in InstagramProfile.objects.all():
        try:
            profile._parse_instagram_data()
        except Exception as e:  # Ловим любые исключения для безопасности
            # Подобный подход можно использовать для логирования ошибок задачи update_instagram_data
            CeleryTaskErrorLog.objects.create(
                task_name='update_instagram_data',
                error_message=str(e)
            )