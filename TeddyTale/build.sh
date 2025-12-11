set -o errexit  # Выход при любой ошибке

cd TeddyTale

# Установка зависимостей Python
pip install -r requirements.txt

# Сборка статических файлов Django
python manage.py collectstatic --noinput

# Применение миграций базы данных
python manage.py migrate