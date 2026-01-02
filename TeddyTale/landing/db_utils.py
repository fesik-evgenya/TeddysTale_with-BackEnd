# landing/db_utils.py
"""
Утилиты для безопасной работы с базой данных Supabase
"""
import logging
from django.db import OperationalError, InterfaceError, connection
from functools import wraps

logger = logging.getLogger(__name__)

def safe_db_query(func):
    """
    Декоратор для безопасного выполнения функций с запросами к БД.
    Автоматически переподключается при ошибках соединения.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 2
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except (OperationalError, InterfaceError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Ошибка БД при вызове {func.__name__}: {e}. Попытка {attempt + 1}/{max_retries}")
                    # Закрываем и переподключаемся
                    connection.close()
                    connection.connect()
                    continue
                else:
                    logger.error(f"Ошибка БД при вызове {func.__name__} после {max_retries} попыток: {e}")
                    raise
            except Exception as e:
                logger.error(f"Неожиданная ошибка в {func.__name__}: {e}")
                raise
    return wrapper