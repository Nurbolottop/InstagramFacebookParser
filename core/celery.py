from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установка переменной окружения Django для файла 'settings' вашего проекта.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Использование настроек 'CELERY' из вашего файла 'settings.py'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач из всех зарегистрированных приложений Django.
app.autodiscover_tasks()