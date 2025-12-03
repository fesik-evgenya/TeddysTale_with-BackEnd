from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('privacy/', views.privacy, name='privacy'),  # Страница конфиденциальности

]