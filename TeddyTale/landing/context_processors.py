from django.conf import settings

def yandex_maps_api_key(request):
    """
    Добавляет ключ Яндекс.Карт в контекст всех шаблонов
    """
    return {
        'YANDEX_MAPS_API_KEY': settings.YANDEX_MAPS_API_KEY,
    }