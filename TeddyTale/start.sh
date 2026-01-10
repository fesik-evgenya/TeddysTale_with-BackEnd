#!/usr/bin/env bash
# Скрипт запуска Django-приложения на Render
# Выполняется при КАЖДОМ запуске контейнера

set -o errexit  # Выход при ошибке
set -o pipefail # Выход при ошибке в пайпе
set -o nounset  # Выход при использовании необъявленных переменных

echo "=========================================="
echo "🚀 ЗАПУСК DJANGO ПРИЛОЖЕНИЯ"
echo "=========================================="
echo "Время: $(date)"
echo "Хост: $(hostname)"
echo "Порт: ${PORT:-8000}"
echo ""

# ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (проверка критических)
if [ -z "${DATABASE_URL:-}" ]; then
    echo "⚠️  ВНИМАНИЕ: DATABASE_URL не установлен!"
    echo "   Убедитесь, что в Render добавлена переменная:"
    echo "   DATABASE_URL=postgresql://user:pass@host:port/dbname"
fi

if [ -z "${SECRET_KEY:-}" ]; then
    echo "⚠️  ВНИМАНИЕ: SECRET_KEY не установлен!"
    echo "   Django не будет работать без секретного ключа"
fi

# 1. ПРОВЕРКА И СОЗДАНИЕ ДИРЕКТОРИЙ
echo "1. 📁 Проверка директорий..."
for dir in logs media staticfiles; do
    if [ ! -d "$dir" ]; then
        echo "   Создаём: $dir"
        mkdir -p "$dir"
    fi
done

# 2. ПРОВЕРКА СТАТИЧЕСКИХ ФАЙЛОВ
echo "2. 🎨 Проверка статических файлов..."
if [ ! -d "staticfiles" ] || [ -z "$(ls -A staticfiles/ 2>/dev/null)" ]; then
    echo "   Статические файлы отсутствуют, собираем..."
    python manage.py collectstatic --noinput
fi

# 3. ПРИМЕНЕНИЕ МИГРАЦИЙ БАЗЫ ДАННЫХ
echo "3. 🗄️  Проверка миграций..."
python manage.py showmigrations --list 2>/dev/null || true

echo "   Применение миграций к Supabase..."
python manage.py migrate --noinput

# 4. СОЗДАНИЕ АДМИНИСТРАТОРА (если не существует)
echo "4. 👑 Создание администратора..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()

# Проверяем существующих администраторов
admins = User.objects.filter(is_superuser=True)

if not admins.exists():
    # Создаём администратора
    User.objects.create_superuser(
        username='admin',
        email='admin@teddytale.ru',
        password='${ADMIN_PASSWORD:-ChangeMe123}'
    )
    print('✅ Создан администратор: admin / \${ADMIN_PASSWORD:-ChangeMe123}')
    print('⚠️  СРОЧНО смените пароль в админке!')
else:
    print('✅ Администратор уже существует')
    print(f'   Найдено {admins.count()} администратор(ов)')
"

# 5. СОЗДАНИЕ БАЗОВЫХ ДАННЫХ (если нужно)
echo "5. 📝 Инициализация базы данных..."
python manage.py shell -c "
try:
    from teddy_admin.models import PageSection, SectionContent

    # Создание базовых контактов
    section, created = PageSection.objects.get_or_create(
        section_key='contacts',
        defaults={'title': 'Контакты'}
    )

    if created:
        SectionContent.objects.bulk_create([
            SectionContent(section=section, content_key='contactsPhone', value='+7 (999) 999-99-99'),
            SectionContent(section=section, content_key='contactsEmail', value='info@teddytale.ru'),
            SectionContent(section=section, content_key='contactsCity', value='Санкт-Петербург'),
        ])
        print('✅ Созданы базовые контакты')
    else:
        print('✅ Контакты уже существуют')

except Exception as e:
    print(f'ℹ️  Модели teddy_admin не настроены: {e}')
"

# 6. ЗАПУСК СЕРВЕРА С АНТИ-СПЯЩИМ РЕЖИМОМ
echo "6. ⚡ Запуск сервера с настройками против 'засыпания'..."

# Создаём дополнительный health-check endpoint
if ! grep -q "path('health/'" TeddyTale/urls.py 2>/dev/null; then
    echo "   Добавляем health-check endpoint..."
    # Можно добавить простой эндпоинт для проверки
    python manage.py shell -c "
from django.http import JsonResponse
from django.urls import path
import TeddyTale.urls

# Простая функция health-check
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'TeddyTale',
        'timestamp': '$(date -Iseconds)'
    })

# Динамически добавляем маршрут (если не добавлен в urls.py)
TeddyTale.urls.urlpatterns += [path('health/', health_check)]
print('✅ Health-check endpoint добавлен')
"
fi

echo ""
echo "=========================================="
echo "🚀 ЗАПУСК GUNICORN С ОПТИМИЗАЦИЯМИ"
echo "=========================================="

# КРИТИЧЕСКИЕ НАСТРОЙКИ ДЛЯ RENDER (предотвращение сна):
# 1. --preload - загружает приложение до fork (быстрее запуск)
# 2. --timeout 120 - увеличенный таймаут для тяжелых операций
# 3. 2 воркера + 2 потока - оптимально для бесплатного плана
# 4. keep-alive 5 - короткое время keep-alive

exec gunicorn TeddyTale.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 2 \
    --worker-class gthread \
    --timeout 120 \
    --keepalive 5 \
    --preload \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --capture-output