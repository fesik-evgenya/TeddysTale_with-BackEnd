from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db import connection
import time
import os
from datetime import datetime

@require_GET
def health_check(request):
    """Упрощенный health-check"""
    try:
        # Проверка базы данных
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')

        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=503)

@require_GET
def ping(request):
    """Простой пинг"""
    return JsonResponse({'status': 'pong'})