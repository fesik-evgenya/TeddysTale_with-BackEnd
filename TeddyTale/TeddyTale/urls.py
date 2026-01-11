from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from .health_views import health_check, ping

# Меняем URL стандартной админки
admin.site.site_url = '/panel/'  # Для ссылок "Вернуться на сайт"

urlpatterns = [
    path('panel/', admin.site.urls),  # Стандартная админка

    # Кастомная админка с префиксом admin-custom/
    path('admin-custom/', include(('teddy_admin.urls_custom', 'teddy_admin'),
                                  namespace='teddy_admin_custom')),
    path('', include(('landing.urls', 'landing'), namespace='landing')),

    # Перенаправления для старых путей
    path('enter-admin-panel/', RedirectView.as_view(
        url='/admin-custom/enter/', permanent=False), name='old-admin-enter'),

    # Health check маршруты
    path('health/', health_check),
    path('health', health_check),
    path('ping/', ping),
    path('ping', ping),
]

# ====================
# Разрешаем обслуживание медиафайлов ВСЕГДА
# ====================

# На Render (production) используем специальный маршрут
if settings.IS_RENDER and not settings.DEBUG:
    # Добавляем маршрут для обслуживания медиа-файлов в production
    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
else:
    # В development используем стандартный способ
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)