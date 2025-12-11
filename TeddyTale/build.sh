set -o errexit  # Выход при любой ошибке

echo "=== Установка зависимостей ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Создание директорий ==="
mkdir -p logs
mkdir -p staticfiles

echo "=== Сбор статических файлов ==="
python manage.py collectstatic --noinput --clear

echo "=== Применение миграций ==="
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "=== Создание суперпользователя ==="
# Проверяем, существует ли суперпользователь
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='admin').exists())" | grep -q "True"; then
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell
    echo "✅ Суперпользователь создан"
else
    echo "✅ Суперпользователь уже существует"
fi

echo "=== Сборка завершена ==="