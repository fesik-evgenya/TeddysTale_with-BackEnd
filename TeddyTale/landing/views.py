import logging

from django.shortcuts import render
from teddy_admin.models import PageSection, SectionContent, ShopItem

# Настройка логгера для отслеживания ошибок
logger = logging.getLogger(__name__)

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

        # 3. Товары магазина
        shop_items = (ShopItem.objects.filter(is_active=True).order_by('slot_number'))
        context['shop_items'] = shop_items

        # Определяем, нужно ли показывать статические карточки
        static_items_count = 9 - shop_items.count()
        if static_items_count > 0:
            context['has_static_shop_items'] = True
        else:
            context['has_static_shop_items'] = False

        # Логируем информацию о товарах для отладки
        logger.debug(f"Загружено товаров из базы: {shop_items.count()}")
        logger.debug(f"Показывать статические карточки: {context['has_static_shop_items']}")

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

        # 5. Контакты - КРИТИЧЕСКИЙ ИСПРАВЛЕННЫЙ БЛОК
        # Устанавливаем значения по умолчанию (всегда в контексте)
        default_contacts = {
            'contacts_city': 'Санкт-Петербург',
            'contacts_address': 'ул. Среднерогатская',
            'contacts_latitude': '59.819987',
            'contacts_longitude': '30.337649',
            'contacts_phone': '+7 (911) 999-99-99',
            'contacts_email': 'example@example.ru',
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
        logger.info(f"Главная страница успешно загружена. Товаров: {shop_items.count()}, " +
                    f"Координаты: {context['contacts_latitude']}, {context['contacts_longitude']}")

    except Exception as e:
        # Детальное логирование ошибки без прерывания работы сайта
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА при загрузке данных главной страницы: {str(e)}",
                     exc_info=True, stack_info=True)

        # Безопасный фоллбэк
        context['static_fallback'] = True

        # Товары - пустой список
        context['shop_items'] = []
        context['has_static_shop_items'] = True

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

def privacy(request):
    """
    Обработчик для страницы политики конфиденциальности
    Простая статическая страница без динамического контента
    """
    return render(request, 'privacy.html')