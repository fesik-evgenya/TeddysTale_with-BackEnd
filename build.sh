set -o errexit

# Установка зависимостей
pip install -r requirements.txt

# Сбор статики
python manage.py collectstatic --noinput

# Применение миграций
python manage.py migrate