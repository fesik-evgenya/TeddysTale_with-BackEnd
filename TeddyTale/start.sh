#!/usr/bin/env bash
# start.sh
set -o errexit

echo "=== Запуск TeddyTale на Render ==="
echo "Версия Python: $(python --version)"
echo "Текущая директория: $(pwd)"
echo "Порт: ${PORT:-8000}"

# Проверка, собрана ли статика
if [ ! -d "staticfiles" ] || [ -z "$(ls -A staticfiles/ 2>/dev/null)" ]; then
    echo "⚠️  Статические файлы не найдены. Собираем..."
    python manage.py collectstatic --noinput
fi

# Проверка необходимых директорий
for dir in logs media staticfiles; do
    if [ ! -d "$dir" ]; then
        echo "⚠️  Директория $dir не найдена. Создаем..."
        mkdir -p "$dir"
    fi
done

# Запуск Gunicorn
echo "🚀 Запуск Gunicorn..."
exec gunicorn TeddyTale.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -