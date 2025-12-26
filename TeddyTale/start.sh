#!/usr/bin/env bash
# start.sh - универсальный скрипт запуска
set -o errexit

echo "=== ЗАПУСК DJANGO ПРИЛОЖЕНИЯ ==="
echo "Порт: ${PORT:-8000}"

# Проверка статики (создаём если нет)
if [ ! -d "staticfiles" ] || [ -z "$(ls -A staticfiles/ 2>/dev/null)" ]; then
    echo "Статические файлы не найдены, собираем..."
    python manage.py collectstatic --noinput
fi

# Проверка необходимых директорий
for dir in logs media staticfiles; do
    if [ ! -d "$dir" ]; then
        echo "Создаём директорию: $dir"
        mkdir -p "$dir"
    fi
done

# Запуск Gunicorn
echo "Запуск сервера..."
exec gunicorn TeddyTale.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -