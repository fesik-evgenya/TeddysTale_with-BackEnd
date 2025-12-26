#!/usr/bin/env bash
# build.sh
set -o errexit

echo "=== Начало сборки TeddyTale на Render ==="
echo "База данных: ${DATABASE_URL##*@}"  # Логируем только хост (без пароля)
date

# 1. Установка зависимостей
echo "1. Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# 2. Проверка структуры проекта
echo "2. Проверка структуры проекта..."
ls -la
ls -la teddy_admin/ || echo "⚠️  Директория teddy_admin не найдена"
ls -la landing/ || echo "⚠️  Директория landing не найдена"

# 3. Создание необходимых директорий
echo "3. Создание директорий..."
mkdir -p logs/audit logs/debug logs/requests
mkdir -p media/shop_items media/uploaded_images
mkdir -p staticfiles/{css,js,assets}

# 4. Проверка и применение миграций
echo "4. Проверка миграций..."
# Сначала смотрим, какие миграции есть
python manage.py showmigrations 2>/dev/null || echo "⚠️  Не удалось проверить миграции"

echo "5. Применение миграций..."
# Применяем миграции для всех приложений
python manage.py migrate --noinput

# 5.1 Явно применяем миграции для teddy_admin (если они существуют)
echo "5.1 Применение миграций для teddy_admin..."
python manage.py migrate teddy_admin --noinput 2>/dev/null || echo "⚠️  Нет миграций для teddy_admin"

# 5.2 Явно применяем миграции для landing (если они существуют)
echo "5.2 Применение миграций для landing..."
python manage.py migrate landing --noinput 2>/dev/null || echo "⚠️  Нет миграций для landing"

# 6. Создание суперпользователя
echo "6. Создание суперпользователя..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@teddystale.ru', 'admin123')
    print('✓ Создан суперпользователь: admin / admin123')
else:
    print('✓ Суперпользователь уже существует')
"

# 7. Сбор статических файлов
echo "7. Сбор статических файлов..."
python manage.py collectstatic --noinput --clear

echo "=== Сборка успешно завершена ==="