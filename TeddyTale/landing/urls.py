from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница

    # Страница конфиденциальности
    path('privacy/', views.privacy, name='privacy'),

]