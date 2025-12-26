#!/bin/bash
# start.sh
set -o errexit

# Запуск Gunicorn
gunicorn TeddyTale.wsgi:application --bind 0.0.0.0:8000