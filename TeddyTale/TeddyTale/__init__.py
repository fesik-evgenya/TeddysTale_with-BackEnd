"""
TeddyTale - Проект интернет-магазина плюшевых медведей

Этот файл инициализирует проект и настраивает логирование.
"""

import os
import logging
from pathlib import Path

# Получаем логгер для этого модуля
logger = logging.getLogger('TeddyTale')

def check_logs_directory():
    """
    Проверяет наличие и доступность папки logs.
    Вызывается при инициализации проекта.
    """
    try:
        # Определяем путь к папке logs относительно этого файла
        base_dir = Path(__file__).resolve().parent.parent
        logs_dir = base_dir / 'logs'

        # Проверяем существование папки (она уже должна быть создана в settings.py)
        if not logs_dir.exists():
            logger.warning(f"Папка logs не существует: {logs_dir}")
            logs_dir.mkdir(exist_ok=True, mode=0o755)
            logger.info(f"Создана папка logs: {logs_dir}")

        # Проверяем права на запись
        test_file = logs_dir / '.write_test'
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            test_file.unlink()
            logger.debug(f"Права на запись в папку logs подтверждены: {logs_dir}")
        except PermissionError as e:
            logger.error(f"Нет прав на запись в папку logs: {logs_dir}. Ошибка: {e}")
            # Пытаемся исправить права (работает только на Unix-системах)
            try:
                os.chmod(logs_dir, 0o755)
                logger.info(f"Права на папку logs исправлены: {logs_dir}")
            except Exception as chmod_error:
                logger.error(f"Не удалось исправить права: {chmod_error}")

        # Создаем подпапки для разных типов логов (опционально)
        subdirs = ['debug', 'audit', 'requests']
        for subdir in subdirs:
            subdir_path = logs_dir / subdir
            subdir_path.mkdir(exist_ok=True, mode=0o755)

        logger.info(f"Папка logs инициализирована: {logs_dir}")
        return True

    except Exception as e:
        logger.error(f"Ошибка при проверке папки logs: {e}", exc_info=True)
        return False

def log_startup_info():
    """Логирует информацию о запуске проекта."""
    import django
    from django.conf import settings

    startup_info = {
        'django_version': django.get_version(),
        'debug_mode': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'database_engine': settings.DATABASES['default']['ENGINE'],
        'time_zone': settings.TIME_ZONE,
        'static_root': getattr(settings, 'STATIC_ROOT', 'Не установлен'),
        'media_root': getattr(settings, 'MEDIA_ROOT', 'Не установлен'),
    }

    logger.info("=" * 50)
    logger.info("Запуск проекта TeddyTale")
    logger.info("=" * 50)

    for key, value in startup_info.items():
        logger.info(f"{key.replace('_', ' ').title()}: {value}")

    logger.info("=" * 50)

# Инициализация при импорте модуля
try:
    # Проверяем папку logs
    logs_ok = check_logs_directory()

    if logs_ok:
        logger.info("Проект TeddyTale успешно инициализирован")
    else:
        logger.warning("Проект TeddyTale инициализирован с проблемами в папке logs")

except Exception as e:
    # Если что-то пошло не так, используем базовое логирование
    logging.basicConfig(level=logging.ERROR)
    logging.error(f"Критическая ошибка при инициализации TeddyTale: {e}", exc_info=True)

# Экспортируем логгер для использования в других модулях
__all__ = ['logger']