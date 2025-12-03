from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

import os


class PageSection(models.Model):
    SECTION_TYPES = [
        ('meta', 'Мета-информация'),
        ('hero', 'Hero-секция'),
        ('shop', 'Магазин товаров'),
        ('about', 'О мастере'),
        ('contacts', 'Контакты'),
    ]

    section_key = models.CharField(max_length=50, unique=True, choices=SECTION_TYPES,
                                                               verbose_name='Ключ секции')
    name = models.CharField(max_length=100, verbose_name='Название секции')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(blank=True, verbose_name='Активна')
    order_index = models.IntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'Секция Страницы'
        verbose_name_plural = 'Секции Страницы'
        ordering = ['order_index']

    def __str__(self):
        return f"{self.name}({self.section_key})"


class SectionContent(models.Model):
    CONTENT_TYPES = [
        ('text', 'Текст (одна строка)'),
        ('textarea', 'Текст (несколько строк)'),
        ('image', 'Изображение'),
        ('url', 'Ссылка (URL)'),
        ('phone', 'Телефон'),
        ('email', 'Email'),
        ('coordinates', 'Координаты'),
    ]

    section = models.ForeignKey(
        PageSection,
        on_delete=models.CASCADE,
        related_name='contents',
        verbose_name='Секция',
    )
    content_key = models.CharField(max_length=50, verbose_name='Ключ контента')
    content_type = models.CharField(max_length=20, verbose_name='Тип контента')
    label = models.CharField(max_length=100, choices=CONTENT_TYPES, verbose_name='Название поля')
    value = models.TextField(blank=True, null=True, verbose_name='Значение')
    placeholder = models.TextField(blank=True, verbose_name='Пример заполнения')
    help_text = models.TextField(blank=True, verbose_name='Подсказка')
    max_length = models.IntegerField(blank=True, null=True, verbose_name='Макс. длина')
    is_required = models.BooleanField(default=True, verbose_name='Обязательное')
    order_index = models.IntegerField(default=0, verbose_name='Порядок')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Элемент контента'
        verbose_name_plural = 'Элемент контента'
        unique_together = ['section', 'content_key']
        ordering = ['order_index']

    def __str__(self):
        return f"{self.section.name} - {self.label}"


class ShopItem(models.Model):
    slot_number = models.IntegerField(unique=True, validators=[MinValueValidator(1), MaxValueValidator(9)],
                                      verbose_name='Номер слота (1-9)')
    title = models.CharField(max_length=200, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание товара')
    price = models.CharField(max_length=50, verbose_name='Цена')

    # изображение товара
    image = models.ImageField(upload_to='shop_items/', verbose_name='Изображение товара')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    order_index = models.IntegerField(default=0, verbose_name='Порядок')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Товар магазина'
        verbose_name_plural = 'Товары магазина'
        ordering = ['slot_number']

    def __str__(self):
        return f"{self.slot_number}. {self.title}"

    def delete(self, *args, **kwargs):
        # удаляем файл изображения при удалении записи
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


class UploadedImage(models.Model):
    original_filename = models.CharField(max_length=255, verbose_name='Исходное имя файла')
    stored_filename = models.CharField(max_length=255, unique=True, verbose_name='Имя в системе')
    file_path = models.CharField(max_length=500, verbose_name='Путь к файлу')
    file_size = models.IntegerField(verbose_name='Размер файла')
    mime_types = models.CharField(max_length=100, verbose_name='Тип файла')

    # размеры изображения
    width = models.IntegerField(blank=True, null=True, verbose_name='Ширина')
    height = models.IntegerField(blank=True, null=True, verbose_name='Высота')

    # для связи с контентом
    section_type = models.CharField(max_length=50, blank=True, verbose_name='Тип секции')
    content_key = models.CharField(max_length=50, blank=True, verbose_name='Ключ контента')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Загрузил')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    last_accessed = models.DateTimeField(null=True, blank=True, verbose_name='Последний доступ')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Загруженное изображение'
        verbose_name_plural = 'Загруженные изображения'

    def __str__(self):
        return self.original_filename


class SiteSettings(models.Model):
    SETTING_TYPES = [
        ('text', 'Текст'),
        ('boolean', 'Да/Нет'),
        ('number', 'Число'),
        ('json', 'JSON'),
    ]

    setting_key = models.CharField(max_length=50, unique=True, verbose_name='Ключ настройки')
    setting_value = models.TextField(blank=True, null=True, verbose_name='Значение')
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='text',
                                                                          verbose_name='Тип значения')
    category = models.CharField(max_length=50, default='general', verbose_name='Категория')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_public = models.BooleanField(default=False, verbose_name='Публичная')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Настройка сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return self.setting_key

class ChangeLog(models.Model):
    ACTIONS = [
        ('CREATE','Создание'),
        ('UPDATE','Обновление'),
        ('DELETE','Удаление'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                                                         verbose_name='Пользователь')
    changed_table = models.CharField(max_length=50, verbose_name='Таблица')
    record_id = models.IntegerField(null=True, blank=True, verbose_name='ID записи')
    action = models.CharField(max_length=10, choices=ACTIONS, verbose_name='Действие')
    old_value = models.TextField(blank=True, null=True, verbose_name='Старое значение')
    new_value = models.TextField(blank=True, null=True, verbose_name='Новое значение')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP адрес')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения')

    class Meta:
        verbose_name = 'Лог изменения'
        verbose_name_plural = 'Логи изменения'

    def __str__(self):
        return f"{self.changed_table} - {self.action} - {self.changed_at}"
