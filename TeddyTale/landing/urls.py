from django.urls import path, include
from django.contrib import admin
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('privacy/', views.privacy, name='privacy'),  # Страница конфиденциальности

]