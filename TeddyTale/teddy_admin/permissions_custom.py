from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

def is_site_admin(user):
    """Проверяет, может ли пользователь использовать кастомную админку
        Возвращает True если пользователь:
        1. Суперпользователь (is_superuser=True)
        2. Входит в группу "SiteAdmins"""
    if not user.is_authenticated:
        return False

    # Суперпользователь имеет доступ ко всему
    if user.is_superuser:
        return True

    # Проверяем группу "SiteAdmins"
    return user.groups.filter(name='SiteAdmins').exists()

def check_site_admin_access(user):
    """Проверка с выбрасыванием исключения"""
    if not is_site_admin(user):
        raise PermissionDenied("У вас нет доступа к админ-панели")
    return True