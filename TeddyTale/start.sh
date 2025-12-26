#!/usr/bin/env bash
# start.sh
set -o errexit

echo "=== Запуск TeddyTale на Render ==="
echo "Текущая директория: $(pwd)"
echo "Порт: ${PORT:-8000}"

# Проверка базы данных
echo "Проверка базы данных..."
python -c "
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TeddyTale.settings')
django.setup()

try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✓ База данных подключена')
except Exception as e:
    print(f'⚠️  Ошибка базы данных: {e}')
"

# Проверка статики
if [ ! -d "staticfiles" ] || [ -z "$(ls -A staticfiles/ 2>/dev/null)" ]; then
    echo "⚠️  Статические файлы не найдены. Собираем..."
    python manage.py collectstatic --noinput
fi

# Запуск Gunicorn
echo "🚀 Запуск Gunicorn..."
exec gunicorn TeddyTale.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -