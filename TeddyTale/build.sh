#!/usr/bin/env bash
# build.sh - универсальный скрипт для деплоя
set -o errexit

echo "=== НАЧАЛО СБОРКИ DJANGO ПРОЕКТА ==="
echo "Хост базы данных: ${DATABASE_URL##*@}"  # Безопасное логирование
date

# 1. Установка зависимостей
echo "1. Установка зависимостей Python..."
pip install --upgrade pip
pip install -r requirements.txt

# 2. Создание необходимых директорий
echo "2. Создание директорий..."
mkdir -p logs media staticfiles
mkdir -p media/shop_items media/uploaded_images 2>/dev/null || true
mkdir -p staticfiles/{css,js,assets} 2>/dev/null || true

# 3. ПРОВЕРКА И СОЗДАНИЕ МИГРАЦИЙ НА СЕРВЕРЕ
echo "3. Проверка миграций..."
python manage.py showmigrations 2>/dev/null || echo "Информация о миграциях недоступна"

# 4. СОЗДАНИЕ МИГРАЦИЙ ЕСЛИ ИХ НЕТ
echo "4. Создание миграций на сервере..."

# Для teddy_admin
if [ ! -d "teddy_admin/migrations" ] || [ -z "$(find teddy_admin/migrations -name '*.py' ! -name '__init__.py' 2>/dev/null)" ]; then
    echo "Создание миграций для teddy_admin..."
    python manage.py makemigrations teddy_admin --noinput 2>/dev/null || echo "Не удалось создать миграции для teddy_admin"
else
    echo "Миграции для teddy_admin уже существуют"
fi

# Для landing
if [ ! -d "landing/migrations" ] || [ -z "$(find landing/migrations -name '*.py' ! -name '__init__.py' 2>/dev/null)" ]; then
    echo "Создание миграций для landing..."
    python manage.py makemigrations landing --noinput 2>/dev/null || echo "Не удалось создать миграции для landing"
else
    echo "Миграции для landing уже существуют"
fi

# 5. ПРИМЕНЕНИЕ ВСЕХ МИГРАЦИЙ
echo "5. Применение миграций к базе данных..."
python manage.py migrate --noinput

# 6. СОЗДАНИЕ СУПЕРПОЛЬЗОВАТЕЛЯ ДЛЯ АДМИНКИ
echo "6. Создание администратора..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='dev').exists():
    User.objects.create_superuser('dev', 'ganef85@mail.ru', 'admin123')
    print('✓ Создан администратор: dev / admin123')
else:
    print('✓ Администратор уже существует')
"

# 7. СОЗДАНИЕ БАЗОВЫХ ДАННЫХ ДЛЯ САЙТА
echo "7. Создание базовых данных для сайта..."
python manage.py shell -c "
try:
    from teddy_admin.models import PageSection, SectionContent

    # Создаём секцию контактов
    contacts_section, created = PageSection.objects.get_or_create(
        section_key='contacts',
        defaults={'title': 'Контакты'}
    )

    if created:
        # Добавляем поля контактов
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
        print('✓ Созданы базовые контакты')
    else:
        print('✓ Контакты уже существуют')

except Exception as e:
    print(f'ℹ️  База данных для teddy_admin не настроена: {e}')
"

# 8. СБОР СТАТИЧЕСКИХ ФАЙЛОВ
echo "8. Сбор статических файлов (CSS, JS, изображения)..."
python manage.py collectstatic --noinput --clear

echo "=== СБОРКА УСПЕШНО ЗАВЕРШЕНА ==="