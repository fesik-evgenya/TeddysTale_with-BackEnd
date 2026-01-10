"""
WSGI config for TeddyTale project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TeddyTale.settings')

# Импортируем и запускаем сервисы ТОЛЬКО на Render
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