"""
Декораторы для кастомной админки Teddy Tale.
Содержит декораторы для проверки прав доступа к админ-панели.
"""

from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from functools import wraps
from .permissions_custom import is_site_admin


# Основной декоратор для проверки прав доступа к кастомной админке
custom_admin_required = user_passes_test(
    is_site_admin,
    login_url='/enter-admin-panel/',
    redirect_field_name=None
)


def custom_admin_required_decorator(view_func):
    """
    Альтернативная реализация декоратора с более подробной логикой.
    Использование: @custom_admin_required_decorator
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            # Если AJAX-запрос - возвращаем JSON ошибку
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Требуется авторизация',
                    'redirect': '/enter-admin-panel/'
                }, status=401)
            # Обычный запрос - редирект на страницу входа
            from django.shortcuts import redirect
            return redirect('/enter-admin-panel/')

        # Проверяем права доступа
        if not is_site_admin(request.user):
            # Если AJAX-запрос - возвращаем JSON ошибку
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Доступ запрещен'
                }, status=403)
            # Обычный запрос - выбрасываем исключение PermissionDenied
            raise PermissionDenied("У вас нет доступа к кастомной админке")

        # Если все проверки пройдены - выполняем представление
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def custom_admin_required_ajax(view_func):
    """
    Декоратор специально для AJAX-запросов.
    Всегда возвращает JSON, даже при ошибках доступа.
    Использование: @custom_admin_required_ajax
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'auth_required',
                'message': 'Требуется авторизация',
                'redirect_url': '/enter-admin-panel/'
            }, status=401)

        # Проверяем права доступа
        if not is_site_admin(request.user):
            return JsonResponse({
                'status': 'permission_denied',
                'message': 'Доступ запрещен. У вас нет прав для этого действия.'
            }, status=403)

        # Добавляем информацию о пользователе в request для удобства
        request.is_admin_user = True
        request.admin_user = request.user

        # Выполняем представление
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def custom_admin_method_required(method_list=None):
    """
    Декоратор для методов, который проверяет права только для указанных HTTP-методов.
    Использование: @custom_admin_method_required(['POST', 'PUT', 'DELETE'])
    """
    if method_list is None:
        method_list = ['POST', 'PUT', 'DELETE', 'PATCH']

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Если метод не в списке проверяемых - пропускаем проверку
            if request.method not in method_list:
                return view_func(request, *args, **kwargs)

            # Для проверяемых методов - проверяем права
            if not request.user.is_authenticated:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Требуется авторизация'
                    }, status=401)
                from django.shortcuts import redirect
                return redirect('/enter-admin-panel/')

            if not is_site_admin(request.user):
                raise PermissionDenied("У вас нет прав для выполнения этого действия")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# Комбинированные декораторы для удобства
def custom_admin_required_with_logging(view_func):
    """
    Декоратор с логированием доступа.
    Использование: @custom_admin_required_with_logging
    """
    @wraps(view_func)
    @custom_admin_required_decorator
    def _wrapped_view(request, *args, **kwargs):
        import logging
        logger = logging.getLogger('teddy_admin.access')

        # Логируем доступ к защищенной странице
        logger.info(
            f"Admin access: user={request.user.username}, "
            f"path={request.path}, method={request.method}, "
            f"ip={request.META.get('REMOTE_ADDR')}"
        )

        # Выполняем представление
        response = view_func(request, *args, **kwargs)

        # Логируем результат
        logger.info(
            f"Admin response: user={request.user.username}, "
            f"path={request.path}, status={response.status_code}"
        )

        return response

    return _wrapped_view


# Класс-декоратор для использования в Class-Based Views
class CustomAdminRequiredMixin:
    """
    Миксин для Class-Based Views.
    Использование в классе: class MyView(CustomAdminRequiredMixin, TemplateView):
    """

    def dispatch(self, request, *args, **kwargs):
        # Проверяем авторизацию
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('/enter-admin-panel/')

        # Проверяем права
        if not is_site_admin(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("У вас нет доступа к кастомной админке")

        # Если все ок - вызываем родительский dispatch
        return super().dispatch(request, *args, **kwargs)


# Утилиты для работы с декораторами
def get_admin_required_decorator(ajax=False, logging=False, methods=None):
    """
    Фабрика декораторов. Возвращает нужный декоратор в зависимости от параметров.

    Параметры:
    - ajax: bool - для AJAX-запросов (возвращает JSON)
    - logging: bool - с логированием доступа
    - methods: list - список методов для проверки (если None - все методы)

    Примеры:
        @get_admin_required_decorator(ajax=True)
        @get_admin_required_decorator(logging=True)
        @get_admin_required_decorator(methods=['POST', 'DELETE'])
    """
    if ajax:
        return custom_admin_required_ajax
    elif logging:
        return custom_admin_required_with_logging
    elif methods is not None:
        return custom_admin_method_required(methods)
    else:
        return custom_admin_required_decorator


# Короткие алиасы для удобства использования
admin_required = custom_admin_required
admin_ajax = custom_admin_required_ajax
admin_logged = custom_admin_required_with_logging
admin_mixin = CustomAdminRequiredMixin


# Экспортируемые декораторы
__all__ = [
    'custom_admin_required',
    'custom_admin_required_decorator',
    'custom_admin_required_ajax',
    'custom_admin_method_required',
    'custom_admin_required_with_logging',
    'CustomAdminRequiredMixin',
    'get_admin_required_decorator',
    'admin_required',
    'admin_ajax',
    'admin_logged',
    'admin_mixin',
]