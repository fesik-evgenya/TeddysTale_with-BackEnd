from django.contrib import admin
from .models import *
from django.utils.html import format_html

class SectionContentInline(admin.TabularInline):
    model = SectionContent
    extra = 0
    fields = ['content_key','label','content_type','value','order_index']
    ordering = ['order_index']

@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ['name','section_key','is_active','order_index']
    list_editable = ['is_active','order_index']
    list_filter = ['is_active','section_key']
    search_fields = ['name','section_key','description']
    inlines = [SectionContentInline]
    ordering = ['order_index']

@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ['slot_number','title','price','image_preview', 'is_active']
    list_editable = ['title', 'price', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    ordering = ['slot_number']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" '
                               'style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'

@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ['original_filename','image_preview','file_size',
                    'uploaded_at', 'is_active']
    list_filter = ['is_active', 'section_type']
    search_fields = ['original_filename', 'stored_filename']
    ordering = ['uploaded_at', 'last_accessed']

    def image_preview(self, obj):
        return format_html('<img src="/media/{}" width="50" height="50"'
                           ' style="object-fit: cover;" / >', obj.file_path)
    image_preview.short_description = 'Превью'

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):  # Изменено имя класса для ясности
    list_display = ['setting_key','setting_value_preview','category',
                    'is_public']
    list_filter = ['category', 'is_public']
    search_fields = ['setting_key', 'description']

    def setting_value_preview(self, obj):
        if obj.setting_value:
            value = obj.setting_value
            if len(value) > 50:
                return value[:50] + '...'
            return value
        return "Не задано"
    setting_value_preview.short_description = 'Значение'

@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ['changed_table','action','user','changed_at']
    list_filter = ['action', 'changed_table', 'changed_at']
    search_fields = ['changed_table', 'user_username']
    readonly_fields = ['changed_at', 'user', 'ip_address', 'user_agent']
    date_hierarchy = 'changed_at'

    def has_add_permission(self, request):
        # запрещаем создание логов вручную
        return False

    def has_change_permission(self, request, obj=None):
        # запрещаем редактирование логов
        return False

@admin.register(SectionContent)
class SectionContentAdmin(admin.ModelAdmin):
    list_display = ['section','content_key','label','content_type',
                    'value_preview']
    list_filter = ['section', 'content_type']
    search_fields = ['label', 'content_key', 'value']
    list_editable = ['label']

    def value_preview(self, obj):
        if obj.value:
            if obj.content_type == 'image':
                return format_html('<img src="/media/{}" width="50"'
                                   ' height="50" />', obj.value)
            value = obj.value
            if len(value) > 50:
                return value[:50] + '...'
            return value
        return "Не задано"
    value_preview.short_description = 'Значение'