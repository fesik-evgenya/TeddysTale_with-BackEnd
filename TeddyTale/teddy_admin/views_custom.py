import json
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.conf import settings
from django.utils import timezone
from uuid import uuid4
from .models import PageSection, ShopItem, SectionContent, ChangeLog, SiteSettings, UploadedImage
from .permissions_custom import is_site_admin, check_site_admin_access


@csrf_protect
@require_http_methods(["GET", "POST"])
def custom_admin_login(request):
    """
    Вход в кастомную админку по адресу /enter-admin-panel/
    """
    # Проверяем аутентификацию, но обрабатываем возможные ошибки сессии
    try:
        # Эта проверка может вызвать ошибку, если сессия была удалена
        user_authenticated = request.user.is_authenticated
    except Exception:
        # Если произошла ошибка при проверке аутентификации,
        # считаем пользователя неаутентифицированным
        user_authenticated = False

    # Если пользователь аутентифицирован и является администратором, перенаправляем
    if user_authenticated and is_site_admin(request.user):
        return redirect('teddy_admin_custom:custom-panel')

    error = None

    # Загружаем контакты из базы данных для футера
    try:
        contacts_section = (PageSection.objects
                            .filter(section_key='contacts').first())
        contacts_contents = {}

        if contacts_section:
            # Получаем содержимое секции контактов
            contents = (SectionContent.objects
                        .filter(section=contacts_section)
                        .order_by('order_index'))
            for content in contents:
                contacts_contents[content.content_key] = {
                    'value': content.value,
                    'label': content.label,
                    'content_type': content.content_type,
                    'id': content.id
                }
    except Exception as e:
        # В случае ошибки используем пустой словарь
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при загрузке контактов для страницы входа: {e}")
        contacts_contents = {}

    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user and is_site_admin(user):
            # Перед входом создаем новую сессию, если старая была удалена
            try:
                # Сохраняем текущую сессию, если она существует
                request.session.save()
            except Exception:
                # Если не удалось сохранить, создаем новую
                pass

            login(request, user)
            # Перенаправляем в кастомную админку
            return redirect('teddy_admin_custom:custom-panel')
        else:
            error = "Неверный логин или пароль"

    # Создаем переменные для футера из contacts_contents
    context = {
        'error': error,
        'contacts_phone': contacts_contents.get('contactsPhone', {})
        .get('value', '+7 (911) 129-26-55'),  # Исправлено
        'contacts_email': contacts_contents.get('contactsEmail', {})
        .get('value', 'ev.filenko@rambler.ru'),  # Исправлено
        'contacts_city': contacts_contents.get('contactsCity', {})
        .get('value', 'Санкт-Петербург'),
        'contacts_address': contacts_contents.get('contactsAddress', {})
        .get('value', 'ул. Среднерогатская'),
        'contacts_vk': contacts_contents.get('contactsVK', {})
        .get('value', ''),
        'contacts_whatsapp': contacts_contents.get('contactsWhatsApp', {})
        .get('value', ''),
        'contacts_telegram': contacts_contents.get('contactsTelegramm', {})
        .get('value', ''),
    }

    return render(request, 'enter-admin-panel.html', context)


@login_required
def custom_admin_panel(request):
    """
    Главная страница кастомной админки по адресу /admin-panel/
    """
    # Проверяем права с обработкой возможных ошибок сессии
    try:
        check_site_admin_access(request.user)
    except Exception as e:
        # Если произошла ошибка при проверке прав (например, сессия удалена),
        # перенаправляем на страницу входа
        return redirect('teddy_admin_custom:custom-login')

    # Получаем все секции (только активные для отображения в админке)
    page_sections = (PageSection.objects.filter(is_active=True)
                     .order_by('order_index'))
    all_sections = PageSection.objects.all().order_by('order_index')
    shop_items = (ShopItem.objects.filter(is_active=True)
                  .order_by('slot_number'))

    # Создаем словарь для хранения содержимого каждой секции
    section_contents = {}

    for section in page_sections:
        contents = (SectionContent.objects.filter(section=section)
                    .order_by('order_index'))
        content_dict = {}
        for content in contents:
            content_dict[content.content_key] = {
                'value': content.value,
                'label': content.label,
                'content_type': content.content_type,
                'id': content.id
            }
        section_contents[section.section_key] = content_dict

    # Получаем контент для каждой секции
    meta_contents = section_contents.get('meta', {})
    hero_contents = section_contents.get('hero', {})
    about_contents = section_contents.get('about', {})
    contacts_contents = section_contents.get('contacts', {})

    # Получаем настройки сайта
    site_settings = {}
    for setting in SiteSettings.objects.all():
        site_settings[setting.setting_key] = setting.setting_value

    # Получаем загруженные изображения
    uploaded_images = UploadedImage.objects.filter(is_active=True)

    # Создаем также отдельные переменные для футера для совместимости
    context = {
        'page_sections': page_sections,
        'shop_items': shop_items,
        'all_sections': all_sections,
        'meta_contents': meta_contents,
        'hero_contents': hero_contents,
        'about_contents': about_contents,
        'contacts_contents': contacts_contents,
        'site_settings': site_settings,
        'uploaded_images': uploaded_images,
        'MEDIA_URL': settings.MEDIA_URL,
        # Добавляем отдельные переменные для футера (для совместимости)
        'contacts_phone': contacts_contents.get('contactsPhone', {})
        .get('value', '+7 (911) 129-26-55'),  # Исправлено
        'contacts_email': contacts_contents.get('contactsEmail', {})
        .get('value', 'ev.filenko@rambler.ru'),  # Исправлено
        'contacts_city': contacts_contents.get('contactsCity', {})
        .get('value', 'Санкт-Петербург'),
        'contacts_address': contacts_contents.get('contactsAddress', {})
        .get('value', 'ул. Среднерогатская'),
        'contacts_vk': contacts_contents.get('contactsVK', {})
        .get('value', ''),
        'contacts_whatsapp': contacts_contents.get('contactsWhatsApp', {})
        .get('value', ''),
        'contacts_telegram': contacts_contents.get('contactsTelegramm', {})
        .get('value', ''),
    }

    return render(request, 'admin-panel.html', context)


def custom_admin_logout(request):
    """
    Выход из кастомной админки
    """
    logout(request)
    return redirect('/')  # Перенаправляем на главную лендинга


@require_POST
@login_required
@csrf_protect
def update_shop_item_ajax(request, item_id):
    """
    AJAX-обновление товара
    """
    check_site_admin_access(request.user)

    try:
        data = json.loads(request.body)
        item = ShopItem.objects.get(id=item_id)

        old_values = {
            'title': item.title,
            'description': item.description,
            'price': item.price,
        }

        if 'title' in data:
            item.title = data['title']
        if 'description' in data:
            item.description = data['description']
        if 'price' in data:
            item.price = data['price']

        item.save()

        ChangeLog.objects.create(
            user=request.user,
            changed_table='ShopItem',
            record_id=item.id,
            action='UPDATE',
            old_value=json.dumps(old_values, ensure_ascii=False),
            new_value=json.dumps({
                'title': item.title,
                'description': item.description,
                'price': item.price,
            }, ensure_ascii=False)
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Товар обновлен',
            'data': {
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'price': item.price,
            }
        })
    except ShopItem.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': f'Товар с ID {item_id} не найден'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Неверный формат JSON данных'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка при обновлении: {str(e)}'
        }, status=400)


@require_POST
@login_required
@csrf_protect
def update_section_content_ajax(request, section_key):
    """
    AJAX-обновление контента секции
    """
    check_site_admin_access(request.user)

    try:
        data = json.loads(request.body)

        content_key = data.get('content_key')
        if not content_key:
            return JsonResponse({
                'status': 'error',
                'message': 'Не указан ключ контента'
            }, status=400)

        # Пытаемся получить секцию, если нет - создаем с логикой для разных секций
        try:
            section = PageSection.objects.get(section_key=section_key)
        except PageSection.DoesNotExist:
            # Создаем секцию в зависимости от типа
            if section_key == 'contacts':
                section = PageSection.objects.create(
                    section_key='contacts',
                    name='Контакты',
                    is_active=True,
                    order_index=4  # После about
                )

                # Автоматически создаем стандартные поля для контактов
                contacts_fields = [
                    ('contactsPhone', 'Телефон', 'tel', '+7 (911) 129-26-55'),
                    ('contactsEmail', 'Email', 'email', 'ev.filenko@rambler.ru'),
                    ('contactsCity', 'Город', 'text', 'Санкт-Петербург'),
                    ('contactsAddress', 'Адрес', 'text', 'ул. Среднерогатская'),
                    ('contactsVK', 'ВКонтакте', 'url', ''),
                    ('contactsWhatsApp', 'WhatsApp', 'tel', ''),
                    ('contactsTelegramm', 'Telegram', 'url', ''),
                    ('mapCoords', 'Координаты карты', 'coordinates', '59.819987,30.337649'),
                ]

                for order_index, (key, label, content_type, default_value) in enumerate(contacts_fields):
                    SectionContent.objects.create(
                        section=section,
                        content_key=key,
                        label=label,
                        content_type=content_type,
                        value=default_value,
                        order_index=order_index
                    )
            else:
                # Для других секций создаем базовую секцию
                section = PageSection.objects.create(
                    section_key=section_key,
                    name=section_key.capitalize(),
                    is_active=True,
                    order_index=999  # В конец списка
                )

        content, created = SectionContent.objects.get_or_create(
            section=section,
            content_key=content_key,
            defaults={
                'label': data.get('label', ''),
                'content_type': data.get('content_type', 'text'),
                'value': data.get('value', ''),
            }
        )

        old_value = content.value

        if 'value' in data:
            content.value = data['value']
        if 'label' in data:
            content.label = data['label']
        if 'content_type' in data:
            content.content_type = data['content_type']

        content.save()

        action = 'CREATE' if created else 'UPDATE'
        ChangeLog.objects.create(
            user=request.user,
            changed_table='SectionContent',
            record_id=content.id,
            action=action,
            old_value=old_value if not created else '',
            new_value=content.value
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Контент обновлен',
            'data': {
                'id': content.id,
                'section': section.name,
                'content_key': content.content_key,
                'label': content.label,
                'value': content.value,
                'created': created,
            }
        })
    except PageSection.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': f'Секция {section_key} не найдена'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Неверный формат JSON данных'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка при обновлении: {str(e)}'
        }, status=400)


@require_POST
@login_required
@csrf_protect
def upload_image_ajax(request):
    """
    AJAX-загрузка изображения для секций (hero, about)
    """
    check_site_admin_access(request.user)

    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'status': 'error',
                'message': 'Файл изображения не найден'
            }, status=400)

        image_file = request.FILES['image']

        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        if image_file.content_type not in allowed_types:
            return JsonResponse({
                'status': 'error',
                'message': 'Неподдерживаемый тип файла. Разрешены: JPEG, PNG, WEBP, GIF'
            }, status=400)

        max_size = 5 * 1024 * 1024
        if image_file.size > max_size:
            return JsonResponse({
                'status': 'error',
                'message': 'Файл слишком большой. Максимальный размер: 5MB'
            }, status=400)

        section_type = request.POST.get('section_type', '')
        content_key = request.POST.get('content_key', '')

        # Генерируем новое имя файла
        original_filename = image_file.name
        file_extension = os.path.splitext(original_filename)[1]
        stored_filename = f"{uuid4().hex}{file_extension}"
        file_path = f"uploaded_images/{stored_filename}"

        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(f"media/{file_path}"), exist_ok=True)

        # Находим все старые изображения для этой секции и ключа контента
        old_images = UploadedImage.objects.filter(
            section_type=section_type,
            content_key=content_key
        )

        # Удаляем старые файлы из файловой системы
        for old_image in old_images:
            if old_image.file_path:
                old_file_path = os.path.join(settings.MEDIA_ROOT, old_image.file_path)
                if os.path.exists(old_file_path):
                    try:
                        os.remove(old_file_path)
                    except Exception as e:
                        # Логируем ошибку, но продолжаем выполнение
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Ошибка при удалении старого файла {old_file_path}: {e}")

        # Удаляем старые записи из базы данных
        old_images.delete()

        # Сохраняем новый файл
        with open(f"media/{file_path}", 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        # Создаем новую запись UploadedImage
        uploaded_image = UploadedImage.objects.create(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=image_file.size,
            mime_type=image_file.content_type,
            section_type=section_type,
            content_key=content_key,
            uploaded_by=request.user,
            uploaded_at=timezone.now()
        )

        # Обновляем SectionContent с новым путем к файлу
        try:
            section = PageSection.objects.get(section_key=section_type)
            section_content, created = SectionContent.objects.get_or_create(
                section=section,
                content_key=content_key,
                defaults={
                    'label': f'Изображение {content_key}',
                    'content_type': 'image',
                    'value': file_path,
                }
            )
            if not created:
                section_content.value = file_path
                section_content.save()
        except PageSection.DoesNotExist:
            pass

        ChangeLog.objects.create(
            user=request.user,
            changed_table='UploadedImage',
            record_id=uploaded_image.id,
            action='CREATE',
            new_value=original_filename
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Изображение загружено',
            'data': {
                'id': uploaded_image.id,
                'original_filename': uploaded_image.original_filename,
                'stored_filename': uploaded_image.stored_filename,
                'file_path': uploaded_image.file_path,
                'file_size': uploaded_image.file_size,
                'url': f"{settings.MEDIA_URL}{uploaded_image.file_path}",
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка при загрузке: {str(e)}'
        }, status=400)


@require_POST
@login_required
@csrf_protect
def upload_shop_item_image_ajax(request, item_id):
    """
    AJAX-загрузка изображения для товара ShopItem
    """
    check_site_admin_access(request.user)

    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'status': 'error',
                'message': 'Файл изображения не найден'
            }, status=400)

        image_file = request.FILES['image']

        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        if image_file.content_type not in allowed_types:
            return JsonResponse({
                'status': 'error',
                'message': 'Неподдерживаемый тип файла. Разрешены: JPEG, PNG, WEBP, GIF'
            }, status=400)

        max_size = 5 * 1024 * 1024  # 5MB
        if image_file.size > max_size:
            return JsonResponse({
                'status': 'error',
                'message': 'Файл слишком большой. Максимальный размер: 5MB'
            }, status=400)

        # Получаем товар
        shop_item = ShopItem.objects.get(id=item_id)

        # Сохраняем информацию о старом изображении
        old_image = shop_item.image

        # Обновляем изображение товара
        shop_item.image = image_file
        shop_item.save()

        # Удаляем старый файл изображения, если он существует
        if old_image and old_image.name:
            old_image_path = os.path.join(settings.MEDIA_ROOT, old_image.name)
            if os.path.isfile(old_image_path):
                try:
                    os.remove(old_image_path)
                except Exception as e:
                    print(f"Ошибка при удалении старого файла: {e}")

        ChangeLog.objects.create(
            user=request.user,
            changed_table='ShopItem',
            record_id=shop_item.id,
            action='UPDATE',
            old_value=str(old_image) if old_image else '',
            new_value=str(shop_item.image)
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Изображение товара загружено',
            'data': {
                'id': shop_item.id,
                'image_url': shop_item.image.url,
                'image_name': shop_item.image.name
                .split('/')[-1] if shop_item.image else '',
            }
        })

    except ShopItem.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': f'Товар с ID {item_id} не найден'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка при загрузке изображения товара: {str(e)}'
        }, status=400)


@require_POST
@login_required
@csrf_protect
def update_site_settings_ajax(request):
    """
    AJAX-обновление настроек сайта
    """
    check_site_admin_access(request.user)

    try:
        data = json.loads(request.body)

        setting_key = data.get('setting_key')
        if not setting_key:
            return JsonResponse({
                'status': 'error',
                'message': 'Не указан ключ настройки'
            }, status=400)

        setting, created = SiteSettings.objects.get_or_create(
            setting_key=setting_key,
            defaults={
                'setting_value': data.get('setting_value', ''),
                'setting_type': data.get('setting_type', 'text'),
                'category': data.get('category', 'general'),
                'description': data.get('description', ''),
            }
        )

        old_value = setting.setting_value

        if 'setting_value' in data:
            setting.setting_value = data['setting_value']
        if 'setting_type' in data:
            setting.setting_type = data['setting_type']
        if 'category' in data:
            setting.category = data['category']
        if 'description' in data:
            setting.description = data['description']

        setting.save()

        action = 'CREATE' if created else 'UPDATE'
        ChangeLog.objects.create(
            user=request.user,
            changed_table='SiteSettings',
            record_id=setting.id,
            action=action,
            old_value=old_value if not created else '',
            new_value=setting.setting_value
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Настройка обновлена',
            'data': {
                'id': setting.id,
                'setting_key': setting.setting_key,
                'setting_value': setting.setting_value,
                'created': created,
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Неверный формат JSON данных'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка при обновлении: {str(e)}'
        }, status=400)