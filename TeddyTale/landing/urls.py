from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница

    # Страница конфиденциальности
    path('privacy/', views.privacy, name='privacy'),
    # Страница 503 - нет доступа к базе данных
    path('service-unavailable/', views.service_unavailable_view, name='service_unavailable'),

]