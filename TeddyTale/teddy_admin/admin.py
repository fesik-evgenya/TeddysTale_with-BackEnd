from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.db import transaction, OperationalError
from .models import *
import time

class SectionContentInline(admin.TabularInline):
    model = SectionContent
    extra = 0
    fields = ['content_key', 'label', 'content_type', 'value', 'order_index']
    ordering = ['order_index']

@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'section_key', 'is_active', 'order_index']
    list_editable = ['is_active', 'order_index']
    list_filter = ['is_active', 'section_key']
    search_fields = ['name', 'section_key', 'description']
    inlines = [SectionContentInline]
    ordering = ['order_index']

@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ['slot_number', 'title', 'price', 'image_preview', 'is_active']
    list_editable = ['title', 'price', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    ordering = ['slot_number']

    # Оптимизация для Supabase
    list_per_page = 15  # Уменьшаем для уменьшения нагрузки
    show_full_result_count = False  # Не считать общее количество для скорости
    preserve_filters = False  # Не сохранять фильтры в сессии
    actions = ['supabase_safe_delete', 'delete_selected']  # Добавляем кастомное действие

    def get_queryset(self, request):
        # Оптимизированный запрос для Supabase - только необходимые поля
        qs = super().get_queryset(request)
        return qs.only('id', 'title', 'price', 'slot_number', 'is_active', 'image')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" '
                               'style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'

    def supabase_safe_delete(self, request, queryset):
        """
        Безопасное удаление для Supabase с обработкой idle timeout
        Удаляет товары по одному с паузами
        """
        deleted_count = 0
        errors = []

        # Удаляем по одному в отдельных транзакциях
        for obj in queryset:
            try:
                # Маленькая транзакция для каждого удаления
                with transaction.atomic():
                    obj.delete()
                    deleted_count += 1

                    # Паузы между удалениями для предотвращения блокировок
                    if deleted_count % 3 == 0:
                        time.sleep(0.3)  # Большая пауза каждые 3 удаления
                    else:
                        time.sleep(0.1)  # Маленькая пауза между другими

            except OperationalError as e:
                # Ошибка соединения с Supabase
                errors.append(f"{obj.title}: ошибка соединения с базой")
                time.sleep(1)  # Пауза при ошибке
            except Exception as e:
                errors.append(f"{obj.title}: {str(e)[:100]}")

        # Формируем сообщение о результате
        if deleted_count > 0:
            self.message_user(
                request,
                f"Успешно удалено {deleted_count} товаров.",
                messages.SUCCESS
            )

        if errors:
            error_msg = f"Ошибки при удалении ({len(errors)} товаров): " + "; ".join(errors[:3])
            if len(errors) > 3:
                error_msg += f" ... и ещё {len(errors) - 3} ошибок"
            self.message_user(request, error_msg, messages.WARNING)

    supabase_safe_delete.short_description = "Удалить выбранные (безопасно для Supabase)"

    def changelist_view(self, request, extra_context=None):
        """
        Переопределяем view для работы с Supabase
        """
        try:
            # Пытаемся выполнить стандартный запрос
            return super().changelist_view(request, extra_context)
        except OperationalError as e:
            # Обработка ошибки соединения с Supabase
            self.message_user(
                request,
                "Временные проблемы с базой данных. Пожалуйста, обновите страницу.",
                messages.ERROR
            )

            # Создаем контекст с пустым списком товаров
            from django.contrib.admin.views.main import ChangeList

            model = self.model
            opts = model._meta

            # Создаем ChangeList без запроса к БД
            cl = ChangeList(
                request, model,
                self.list_display,
                self.list_display_links,
                self.list_filter,
                self.date_hierarchy,
                self.search_fields,
                self.list_select_related,
                self.list_per_page,
                self.list_max_show_all,
                self.list_editable,
                model_admin=self,
            )

            # Устанавливаем пустой queryset
            cl.result_list = []
            cl.result_count = 0

            context = {
                **self.admin_site.each_context(request),
                'title': cl.title,
                'cl': cl,
                'media': self.media,
                'has_add_permission': self.has_add_permission(request),
                'opts': opts,
                'app_label': opts.app_label,
                'preserved_filters': self.get_preserved_filters(request),
            }

            return self.render_change_list(request, context, cl)

@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'image_preview', 'file_size',
                    'uploaded_at', 'is_active']
    list_filter = ['is_active', 'section_type']
    search_fields = ['original_filename', 'stored_filename']
    ordering = ['uploaded_at', 'last_accessed']

    def image_preview(self, obj):
        return format_html('<img src="/media/{}" width="50" height="50"'
                           ' style="object-fit: cover;" />', obj.file_path)
    image_preview.short_description = 'Превью'

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['setting_key', 'setting_value_preview', 'category',
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
    list_display = ['changed_table', 'action', 'user', 'changed_at']
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
    list_display = ['section', 'content_key', 'label', 'content_type',
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