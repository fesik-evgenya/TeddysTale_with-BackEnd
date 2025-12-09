from django.urls import path, include
from django.contrib import admin
from . import views_custom

app_name = 'teddy_admin'

urlpatterns = [
    # Стандартная Django админка по адресу /panel/
    path('panel/', admin.site.urls, name='django-admin'),

    # Кастомная админка
    path('', views_custom.custom_admin_login, name='custom-login'),
    path('admin-panel/', views_custom.custom_admin_panel, name='custom-panel'),
    path('logout/', views_custom.custom_admin_logout, name='custom-logout'),
]