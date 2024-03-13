# Используем официальный образ Python как родительский образ
FROM python:3.10

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей проекта и устанавливаем их
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта в контейнер
COPY . .

# Задаем переменную окружения для Django
ENV PYTHONUNBUFFERED 1

# Создаем скрипт для запуска, который сначала выполняет миграции, а затем запускает сервер
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Открываем порт 8000 для доступа к серверу Django извне контейнера
EXPOSE 8000

# Запускаем скрипт при старте контейнера
ENTRYPOINT ["entrypoint.sh"]
