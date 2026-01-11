from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

def is_site_admin(user):
    """Проверяет, может ли пользователь использовать кастомную админку"""
    if not user.is_authenticated:
        return False

    # Суперпользователь имеет доступ ко всему
    if user.is_superuser:
        return True

    # Проверяем группу "SiteAdmins"
    if user.groups.filter(name='SiteAdmins').exists():
        return True

    return False

def check_site_admin_access(user):
    """
    Проверяет, имеет ли пользователь доступ к админке сайта.
    Вызывает PermissionDenied, если доступ запрещен.
    """
    if not user.is_authenticated:
        raise PermissionDenied("Пользователь не аутентифицирован")

    if not is_site_admin(user):
        raise PermissionDenied("Недостаточно прав для доступа к админке")

    return True