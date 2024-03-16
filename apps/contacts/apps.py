from django.apps import AppConfig


class ContactsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contacts'
    verbose_name = "Добавление профиля (Instagram)"

    def ready(self):
        # Импорт сигналов
        import apps.contacts.signals