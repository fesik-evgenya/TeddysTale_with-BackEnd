import threading
import time
import requests
import os
import logging

logger = logging.getLogger(__name__)

class SelfPingService:
    """Сервис для периодического самопина на Render"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.is_running = False
            self.thread = None
            self.ping_interval = 420  # 7 минут (меньше 15-минутного таймаута Render)
            self._initialized = True

    def _ping_loop(self):
        """Цикл периодического пинга"""
        render_url = os.environ.get('RENDER_EXTERNAL_URL')
        if not render_url:
            logger.warning("RENDER_EXTERNAL_URL not set, skipping self-ping")
            return

        while self.is_running:
            try:
                # Пингуем эндпоинт ping (он самый легкий)
                response = requests.get(f"{render_url}/ping", timeout=30)
                if response.status_code == 200:
                    logger.debug(f"Self-ping successful: {response.json().get('status')}")
                else:
                    logger.warning(f"Self-ping failed with status: {response.status_code}")
            except requests.exceptions.Timeout:
                logger.warning("Self-ping timeout")
            except Exception as e:
                logger.error(f"Self-ping error: {e}")

            # Ждем заданный интервал
            for _ in range(self.ping_interval // 10):
                if not self.is_running:
                    return
                time.sleep(10)

    def start(self):
        """Запускает self-ping сервис"""
        if not self.is_running and os.environ.get('RENDER'):
            self.is_running = True
            self.thread = threading.Thread(target=self._ping_loop, daemon=True)
            self.thread.start()
            logger.info("Self-ping service started on Render")

    def stop(self):
        """Останавливает self-ping сервис"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Self-ping service stopped")

# Глобальный экземпляр
self_ping_service = SelfPingService()