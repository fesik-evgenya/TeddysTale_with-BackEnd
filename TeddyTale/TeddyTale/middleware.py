# TeddyTale/middleware.py
"""
Middleware для обработки ошибок соединения с Supabase
"""
import time
import logging
from django.db import connection, connections, OperationalError, InterfaceError
from django.http import HttpResponseServerError

logger = logging.getLogger(__name__)

class SupabaseConnectionMiddleware:
    """
    Middleware для обработки проблем с подключением к Supabase
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Проверяем и восстанавливаем соединение если нужно
            self._ensure_db_connection()

            # Выполняем запрос
            response = self.get_response(request)

            return response

        except (OperationalError, InterfaceError) as e:
            logger.error(f"Ошибка БД Supabase: {e}")

            # Пытаемся восстановить соединение и повторить запрос
            try:
                self._reconnect_all()
                response = self.get_response(request)
                return response
            except Exception as retry_error:
                logger.error(f"Не удалось восстановить соединение: {retry_error}")
                # Возвращаем страницу с ошибкой вместо падения
                return self._get_error_response(request)

    def _ensure_db_connection(self):
        """Проверяет и восстанавливает соединение с БД перед запросом"""
        try:
            for conn_name in connections:
                conn = connections[conn_name]
                # Проверяем, есть ли соединение и активно ли оно
                if conn.connection is None:
                    logger.debug(f"Соединение {conn_name} отсутствует, создаем новое")
                    conn.connect()
                elif hasattr(conn, 'is_usable') and not conn.is_usable():
                    logger.debug(f"Соединение {conn_name} неактивно, переподключаемся")
                    conn.close()
                    conn.connect()
        except Exception as e:
            logger.warning(f"Ошибка при проверке соединения: {e}")
            # Не падаем, пытаемся продолжить

    def _reconnect_all(self):
        """Переподключает все соединения к БД"""
        try:
            for conn_name in connections:
                conn = connections[conn_name]
                conn.close()
                conn.connect()
            logger.info("Все соединения с БД переподключены")
        except Exception as e:
            logger.error(f"Ошибка при переподключении соединений: {e}")
            raise

    def _get_error_response(self, request):
        """Возвращает простую HTML страницу с ошибкой"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Временные проблемы</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: #d32f2f; }
            </style>
        </head>
        <body>
            <h1 class="error">Временные проблемы с базой данных</h1>
            <p>Пожалуйста, попробуйте обновить страницу через несколько секунд.</p>
            <p>Если проблема сохраняется, попробуйте позже.</p>
        </body>
        </html>
        """
        return HttpResponseServerError(html)