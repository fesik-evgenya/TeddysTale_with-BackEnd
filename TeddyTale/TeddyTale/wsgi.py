"""
WSGI config for TeddyTale project.
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TeddyTale.settings')

# Импортируем и запускаем сервисы на Render
if os.environ.get('RENDER'):
    try:
        from .connection_manager import connection_manager
        from .self_ping import self_ping_service

        # Запускаем сервисы
        connection_manager.start()
        self_ping_service.start()
        print("✅ Background services started on Render")

        # Также запускаем функцию инициализации из settings
        from django.conf import settings
        if hasattr(settings, 'initialize_render_specific_settings'):
            settings.initialize_render_specific_settings()

    except ImportError as e:
        print(f"⚠️ Could not import background services: {e}")
    except Exception as e:
        print(f"⚠️ Failed to start background services: {e}")
else:
    print("🟡 Running in local development mode (Render services disabled)")

application = get_wsgi_application()

# ====================
# НАСТРОЙКА WHITENOISE ДЛЯ МЕДИА-ФАЙЛОВ НА RENDER
# ====================

# Определяем режим работы
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
IS_RENDER = os.environ.get('RENDER') is not None

# Получаем базовую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Настраиваем WhiteNoise для статических файлов
application = WhiteNoise(
    application,
    root=os.path.join(BASE_DIR, 'staticfiles'),
    prefix='/static/'
)

# ✅ Добавляем медиа-файлы в WhiteNoise
if IS_RENDER or not DEBUG:
    media_root = os.path.join(BASE_DIR, 'media')
    if os.path.exists(media_root):
        application.add_files(media_root, prefix='/media/')
        print(f"✅ WhiteNoise настроен для обслуживания медиа-файлов на {'' if DEBUG else 'production'} режиме")
    else:
        print(f"⚠️ Медиа директория не найдена: {media_root}")