from django.shortcuts import render

def index(request):
    """Обработчик для главной страницы"""
    return render(request, 'index.html')

def privacy(request):
    """Обработчик для страницы конфиденциальности"""
    return render(request, 'privacy.html')
