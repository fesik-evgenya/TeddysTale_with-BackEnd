# TeddyTale/health_views.py
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_http_methods
from django.db import connection
import time
import os
from datetime import datetime

@require_http_methods(["GET", "HEAD"])  # Разрешаем и GET, и HEAD
def health_check(request):
    """Упрощенный health-check с поддержкой HEAD запросов"""
    try:
        # Проверка базы данных
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')

        if request.method == 'HEAD':
            # Для HEAD запроса возвращаем только заголовки
            response = HttpResponse(status=200)
            response['X-Status'] = 'healthy'
            response['X-Database'] = 'connected'
            return response

        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        }, status=200)
    except Exception as e:
        if request.method == 'HEAD':
            response = HttpResponse(status=503)
            response['X-Status'] = 'unhealthy'
            response['X-Error'] = str(e)[:100]  # Ограничиваем длину ошибки
            return response

        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=503)

@require_http_methods(["GET", "HEAD"])  # Разрешаем и GET, и HEAD
def ping(request):
    """Простой пинг с поддержкой HEAD запросов"""
    if request.method == 'HEAD':
        response = HttpResponse(status=200)
        response['X-Status'] = 'pong'
        return response
    return JsonResponse({'status': 'pong'})