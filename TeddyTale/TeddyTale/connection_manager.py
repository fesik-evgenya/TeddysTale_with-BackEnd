import threading
import time
import logging
from django.db import connection, connections
from django.db.utils import OperationalError, InterfaceError
import os

logger = logging.getLogger(__name__)

class SupabaseConnectionManager:
    """Менеджер для поддержания активного соединения с Supabase"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.is_running = False
            self.thread = None
            self.check_interval = 240  # 4 минуты
            self._initialized = True

    def _check_connection(self):
        """Проверяет и восстанавливает соединение"""
        try:
            # Проверяем основное соединение
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            return True
        except (OperationalError, InterfaceError) as e:
            logger.warning(f"Supabase connection issue: {str(e)[:100]}")
            try:
                # Закрываем и переподключаем
                connection.close()
                connection.connect()
                logger.info("Supabase connection reestablished")
                return True
            except Exception as reconnect_error:
                logger.error(f"Failed to reconnect: {reconnect_error}")
                return False
        except Exception as e:
            logger.error(f"Unexpected connection error: {e}")
            return False

    def _run_checks(self):
        """Основной цикл проверок"""
        while self.is_running:
            try:
                self._check_connection()
            except Exception as e:
                logger.error(f"Error in connection check loop: {e}")

            # Ждем перед следующей проверкой
            for _ in range(self.check_interval // 10):
                if not self.is_running:
                    return
                time.sleep(10)

    def start(self):
        """Запускает менеджер соединений"""
        if not self.is_running and os.environ.get('RENDER'):
            self.is_running = True
            self.thread = threading.Thread(target=self._run_checks, daemon=True)
            self.thread.start()
            logger.info("Supabase Connection Manager started on Render")

    def stop(self):
        """Останавливает менеджер соединений"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Supabase Connection Manager stopped")

# Глобальный экземпляр
connection_manager = SupabaseConnectionManager()