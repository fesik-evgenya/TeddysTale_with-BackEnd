import logging

from django.shortcuts import render
from teddy_admin.models import PageSection, SectionContent, ShopItem
from .db_utils import safe_db_query  # Импортируем декоратор для безопасных запросов

# Настройка логгера для отслеживания ошибок
logger = logging.getLogger(__name__)

@safe_db_query
def index(request):
    """
    Обработчик главной страницы с динамическим контентом
    Использует безопасные значения по умолчанию и подробное логирование
    """
    context = {}

    try:
        # 1. Мета-информация (для <title> и мета-тегов)
        meta_section = PageSection.objects.filter(section_key='meta').first()
        if meta_section:
            meta_contents = {c.content_key: c.value for c in meta_section.contents.all()}
            context['meta_title'] = meta_contents.get('title', 'Мишки Тедди ручной работы')
            context['meta_description'] = meta_contents.get('description',
                                                            'Авторские мишки Тедди ручной работы для вашей коллекции. ' +
                                                            'Уникальные художественные медведи из мохера и традиционных материалов. ' +
                                                            'Закажите своего эксклюзивного Тедди у мастера')
            context['meta_keywords'] = meta_contents.get('keyWords',
                                                         'коллекционные мишки тедди, авторский мишка тедди, медведи тедди ручной работы, ' +
                                                         'мишки тедди на заказ, эксклюзивный мишка тедди, тедди для коллекции')
        else:
            context['meta_title'] = 'Мишки Тедди ручной работы'
            context['meta_description'] = 'Авторские мишки Тедди ручной работы для вашей коллекции'
            context['meta_keywords'] = 'коллекционные мишки тедди, авторский мишка тедди'

        # 2. Hero-секция (главный баннер)
        hero_section = PageSection.objects.filter(section_key='hero').first()
        if hero_section:
            hero_contents = {c.content_key: c.value for c in hero_section.contents.all()}
            context['hero_title'] = hero_contents.get('titleHero', 'Уникальные мишки Тедди с душой')
            context['hero_description'] = hero_contents.get('descriptionHero',
                                                            'Ручная работа, наполненная теплом и заботой. ' +
                                                            'Каждый мишка — это отдельная история, созданная специально для вас.')
            context['hero_image'] = hero_contents.get('heroImage', '')
        else:
            context['hero_title'] = 'Уникальные мишки Тедди с душой'
            context['hero_description'] = ('Ручная работа, наполненная теплом и заботой. ' +
                                           'Каждый мишка — это отдельная история, созданная специально для вас.')
            context['hero_image'] = ''

        # 3. Товары магазина - ОСНОВНОЕ ИЗМЕНЕНИЕ
        shop_items = list(ShopItem.objects.filter(is_active=True).order_by('slot_number'))
        context['shop_items'] = shop_items

        # Определяем, сколько товаров из БД
        db_items_count = len(shop_items)

        # Создаем список из 9 элементов для отображения
        # Сначала добавляем все товары из БД, затем заглушки до 9
        display_items = []
        placeholder_count = 0

        # Добавляем реальные товары из БД
        for i, item in enumerate(shop_items):
            if i < 9:  # Ограничиваем 9 слотами
                display_items.append({
                    'type': 'real',
                    'item': item,
                    'index': i
                })

        # Добавляем заглушки до 9 элементов
        for i in range(db_items_count, 9):
            display_items.append({
                'type': 'placeholder',
                'index': i
            })
            placeholder_count += 1

        context['display_items'] = display_items
        context['has_placeholders'] = placeholder_count > 0

        # Логируем информацию о товарах для отладки
        logger.debug(f"Загружено товаров из базы: {db_items_count}")
        logger.debug(f"Показывать заглушки: {placeholder_count > 0}, количество: {placeholder_count}")

        # 4. Секция "О мастере"
        about_section = PageSection.objects.filter(section_key='about').first()
        if about_section:
            about_contents = {c.content_key: c.value for c in about_section.contents.all()}
            context['about_title1'] = about_contents.get('aboutTitleBlock1', 'История мастера')
            context['about_description1'] = about_contents.get('aboutDescriptionBlock1',
                                                               'Добро пожаловать в мой мир handmade-творчества! Уже более 5 лет я создаю ' +
                                                               'уникальных мишек Тедди, каждый из которых становится особенным другом для ' +
                                                               'своего владельца. Моя философия — это внимание к деталям, использование только ' +
                                                               'качественных материалов и вложение души в каждое творение.')
            context['about_description2'] = about_contents.get('aboutDescriptionBlock2',
                                                               'Моя философия — это внимание к деталям, использование только качественных материалов ' +
                                                               'и вложение души в каждое творение.')
            context['about_title2'] = about_contents.get('aboutTitleBlock2', 'Почему мне доверяют')
            context['about_item1'] = about_contents.get('aboutSlot1Block2', '5+ лет опыта в создании мишек Тедди')
            context['about_item2'] = about_contents.get('aboutSlot2Block2', '200+ довольных клиентов')
            context['about_item3'] = about_contents.get('aboutSlot3Block2', 'Натуральные материалы премиум-класса')
            context['about_item4'] = about_contents.get('aboutSlot4Block2', 'Индивидуальный подход к каждому заказу')
            context['about_image'] = about_contents.get('aboutImage', '')
        else:
            context['about_title1'] = 'История мастера'
            context['about_description1'] = ('Добро пожаловать в мой мир handmade-творчества! Уже более 5 ' +
                                             'лет я создаю уникальных мишек Тедди, каждый из которых ' +
                                             'становится особенным другом для своего владельца. Моя философия ' +
                                             '— это внимание к деталям, использование только качественных ' +
                                             'материалов и вложение души в каждое творение.')
            context['about_description2'] = ('Моя философия — это внимание к деталям, использование только ' +
                                             'качественных материалов и вложение души в каждое творение.')
            context['about_title2'] = 'Почему мне доверяют'
            context['about_item1'] = '5+ лет опыта в создании мишек Тедди'
            context['about_item2'] = '200+ довольных клиентов'
            context['about_item3'] = 'Натуральные материалы премиум-класса'
            context['about_item4'] = 'Индивидуальный подход к каждому заказу'
            context['about_image'] = ''

        # 5. Контакты
        # Устанавливаем значения по умолчанию (всегда в контексте)
        default_contacts = {
            'contacts_city': 'Санкт-Петербург',
            'contacts_address': 'ул. Среднерогатская',
            'contacts_latitude': '59.819987',
            'contacts_longitude': '30.337649',
            'contacts_phone': '+7 (911) 129-26-55',
            'contacts_email': 'ev.filenko@rambler.ru',
            'contacts_vk': 'https://vk.com/id39146412',
            'contacts_whatsapp': 'https://wa.me/79111292655',
            'contacts_telegram': 'https://t.me/Elen0Fil',
        }

        # Добавляем все значения по умолчанию в контекст
        context.update(default_contacts)

        # Пытаемся получить данные из базы
        contacts_section = PageSection.objects.filter(section_key='contacts').first()

        if contacts_section:
            contacts_contents = {c.content_key: c.value for c in contacts_section.contents.all()}

            if contacts_contents:  # Если в секции есть данные
                # Обновляем только те поля, которые есть в базе
                context['contacts_city'] = contacts_contents.get('contactsCity', default_contacts['contacts_city'])
                context['contacts_address'] = contacts_contents.get('contactsAddress', default_contacts['contacts_address'])
                context['contacts_latitude'] = contacts_contents.get('contactsPoints_latitude', default_contacts['contacts_latitude'])
                context['contacts_longitude'] = contacts_contents.get('contactsPoints_longitude', default_contacts['contacts_longitude'])
                context['contacts_phone'] = contacts_contents.get('contactsPhone', default_contacts['contacts_phone'])
                context['contacts_email'] = contacts_contents.get('contactsEmail', default_contacts['contacts_email'])
                context['contacts_vk'] = contacts_contents.get('contactsVK', default_contacts['contacts_vk'])
                context['contacts_whatsapp'] = contacts_contents.get('contactsWhatsApp', default_contacts['contacts_whatsapp'])
                context['contacts_telegram'] = contacts_contents.get('contactsTelegramm', default_contacts['contacts_telegram'])

                logger.debug(f"Контакты из базы данных: {len(contacts_contents)} записей")
            else:
                logger.warning("Секция 'contacts' найдена, но содержимое пустое. Используются значения по умолчанию")
        else:
            logger.warning("Секция 'contacts' не найдена в базе данных, используются значения по умолчанию")

        # Общая информация о загрузке
        logger.info(f"Главная страница успешно загружена. Товаров: {db_items_count}, " +
                    f"Координаты: {context['contacts_latitude']}, {context['contacts_longitude']}")

    except Exception as e:
        # Детальное логирование ошибки без прерывания работы сайта
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА при загрузке данных главной страницы: {str(e)}",
                     exc_info=True, stack_info=True)

        # Безопасный фоллбэк - все 9 карточек как заглушки
        context['static_fallback'] = True
        context['shop_items'] = []
        context['has_placeholders'] = True

        # Создаем список из 9 заглушек
        display_items = []
        for i in range(9):
            display_items.append({
                'type': 'placeholder',
                'index': i
            })
        context['display_items'] = display_items

        # Критически важные значения для работы сайта
        context['meta_title'] = 'Мишки Тедди ручной работы'
        context['hero_title'] = 'Уникальные мишки Тедди с душой'

        # Убедимся, что контакты есть даже в режиме ошибки
        if 'contacts_city' not in context:
            context.update({
                'contacts_city': 'Санкт-Петербург',
                'contacts_latitude': '59.819987',
                'contacts_longitude': '30.337649',
            })

        logger.warning("Используется резервный режим с безопасными значениями")

    return render(request, 'index.html', context)

@safe_db_query
def privacy(request):
    """
    Обработчик для страницы политики конфиденциальности
    с динамическими контактами из базы данных
    """
    # Устанавливаем значения по умолчанию
    default_contacts = {
        'contacts_city': 'Санкт-Петербург',
        'contacts_address': 'ул. Среднерогатская',
        'contacts_phone': '+7 (911) 129-26-55',
        'contacts_email': 'ev.filenko@rambler.ru',
        'contacts_vk': '',
        'contacts_whatsapp': '',
        'contacts_telegram': '',
    }

    context = {}

    try:
        # Пытаемся получить контакты из базы данных
        contacts_section = PageSection.objects.filter(section_key='contacts').first()

        if contacts_section:
            # Получаем содержимое секции контактов
            contacts_contents = {c.content_key: c.value for c in contacts_section.contents.all()}

            # Обновляем контекст данными из базы
            context['contacts_city'] = contacts_contents.get('contactsCity', default_contacts['contacts_city'])
            context['contacts_address'] = contacts_contents.get('contactsAddress', default_contacts['contacts_address'])
            context['contacts_phone'] = contacts_contents.get('contactsPhone', default_contacts['contacts_phone'])
            context['contacts_email'] = contacts_contents.get('contactsEmail', default_contacts['contacts_email'])

            # Дополнительные контакты (могут быть пустыми)
            context['contacts_vk'] = contacts_contents.get('contactsVK', '')
            context['contacts_whatsapp'] = contacts_contents.get('contactsWhatsApp', '')
            context['contacts_telegram'] = contacts_contents.get('contactsTelegramm', '')

            logger.debug(f"Контакты для страницы privacy загружены из базы данных")
        else:
            # Если секция не найдена, используем значения по умолчанию
            context.update(default_contacts)
            logger.warning("Секция 'contacts' не найдена в базе данных, используются значения по умолчанию для страницы privacy")

    except Exception as e:
        # В случае ошибки используем значения по умолчанию
        logger.error(f"Ошибка при загрузке контактов для страницы privacy: {str(e)}",
                     exc_info=True, stack_info=True)
        context.update(default_contacts)
        logger.warning("Используются резервные данные контактов для страницы privacy")

    return render(request, 'privacy.html', context)