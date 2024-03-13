#!/bin/sh

# Применяем миграции Django
python manage.py migrate --noinput

# Собираем статические файлы
python manage.py collectstatic --noinput

# Запускаем сервер разработки Django
exec python manage.py runserver 0.0.0.0:8000