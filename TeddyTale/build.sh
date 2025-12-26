#!/usr/bin/env bash
# build.sh
set -o errexit

echo "=== Начало сборки TeddyTale на Render ==="
date

# 1. Установка зависимостей
echo "1. Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# 2. Создание необходимых директорий
echo "2. Создание директорий..."
mkdir -p logs/audit logs/debug logs/requests
mkdir -p media/shop_items media/uploaded_images
mkdir -p staticfiles/{css,js,assets}  # Используем brace expansion

# 3. Применение миграций
echo "3. Применение миграций..."
python manage.py migrate --noinput

# 4. Создание суперпользователя по умолчанию (если нет)
echo "4. Проверка суперпользователя..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@teddystale.ru', 'admin123')
    print('✓ Создан суперпользователь: admin / admin123')
else:
    print('✓ Суперпользователь уже существует')
"

# 5. Создание базовых данных если база пуста
echo "5. Создание базовых данных..."
python manage.py shell -c "
from teddy_admin.models import PageSection, SectionContent
import os

# Создаем секцию контактов если ее нет
contacts_section, created = PageSection.objects.get_or_create(
    section_key='contacts',
    defaults={'title': 'Контакты'}
)

if created:
    # Создаем поля для контактов
    SectionContent.objects.bulk_create([
        SectionContent(section=contacts_section, content_key='contactsCity', value='Санкт-Петербург'),
        SectionContent(section=contacts_section, content_key='contactsAddress', value='ул. Среднерогатская'),
        SectionContent(section=contacts_section, content_key='contactsPhone', value='+7 (911) 999-99-99'),
        SectionContent(section=contacts_section, content_key='contactsEmail', value='example@example.ru'),
        SectionContent(section=contacts_section, content_key='contactsVK', value='https://vk.com/id39146412'),
        SectionContent(section=contacts_section, content_key='contactsWhatsApp', value='https://wa.me/79111292655'),
        SectionContent(section=contacts_section, content_key='contactsTelegramm', value='https://t.me/Elen0Fil'),
        SectionContent(section=contacts_section, content_key='contactsPoints_latitude', value='59.819987'),
        SectionContent(section=contacts_section, content_key='contactsPoints_longitude', value='30.337649'),
    ])
    print('✓ Создана секция контактов с базовыми данными')
else:
    print('✓ Секция контактов уже существует')
"

# 6. Сбор статических файлов
echo "6. Сбор статических файлов..."
python manage.py collectstatic --noinput --clear

echo "=== Сборка успешно завершена ==="