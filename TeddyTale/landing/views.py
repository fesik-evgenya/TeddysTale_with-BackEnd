from django.shortcuts import render
from teddy_admin.models import PageSection, SectionContent, ShopItem
import logging

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
                                                         'коллекционные мишки тедди, авторский мишка тедди, ' +
                                                         'медведи тедди ручной работы, мишки тедди на заказ, ' +
                                                         'эксклюзивный мишка тедди, тедди для коллекции')
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
        else:
            context['hero_title'] = 'Уникальные мишки Тедди с душой'
            context['hero_description'] = 'Ручная работа, наполненная теплом и заботой. ' + \
                                          'Каждый мишка — это отдельная история, созданная специально для вас.'

        # 3. Товары магазина
        shop_items = ShopItem.objects.filter(is_active=True).order_by('slot_number')
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
                                                               'уникальных мишек Тедди, каждый из которых становится особенным другом ' +
                                                               'для своего владельца. Моя философия — это внимание к деталям, ' +
                                                               'использование только качественных материалов и вложение души в каждое творение.')
            context['about_title2'] = about_contents.get('aboutTitleBlock2', 'Почему мне доверяют')
            context['about_item1'] = about_contents.get('aboutSlot1Block2', '5+ лет опыта в создании мишек Тедди')
            context['about_item2'] = about_contents.get('aboutSlot2Block2', '200+ довольных клиентов')
            context['about_item3'] = about_contents.get('aboutSlot3Block2', 'Натуральные материалы премиум-класса')
            context['about_item4'] = about_contents.get('aboutSlot4Block2', 'Индивидуальный подход к каждому заказу')
        else:
            context['about_title1'] = 'История мастера'
            context['about_description1'] = 'Добро пожаловать в мой мир handmade-творчества! Уже более 5 лет я создаю ' + \
                                            'уникальных мишек Тедди, каждый из которых становится особенным другом ' + \
                                            'для своего владельца. Моя философия — это внимание к деталям, ' + \
                                            'использование только качественных материалов и вложение души в каждое творение.'
            context['about_title2'] = 'Почему мне доверяют'
            context['about_item1'] = '5+ лет опыта в создании мишек Тедди'
            context['about_item2'] = '200+ довольных клиентов'
            context['about_item3'] = 'Натуральные материалы премиум-класса'
            context['about_item4'] = 'Индивидуальный подход к каждому заказу'

        # 5. Контакты
        contacts_section = PageSection.objects.filter(section_key='contacts').first()
        if contacts_section:
            contacts_contents = {c.content_key: c.value for c in contacts_section.contents.all()}

            # Город и адрес
            context['contacts_city'] = contacts_contents.get('contactsCity', 'Санкт-Петербург')
            context['contacts_address'] = contacts_contents.get('contactsAddress', 'ул. Среднерогатская')

            # Координаты для карты
            context['contacts_latitude'] = contacts_contents.get('contactsPoints_latitude', '59.819987')
            context['contacts_longitude'] = contacts_contents.get('contactsPoints_longitude', '30.337649')

            # Контактная информация
            context['contacts_phone'] = contacts_contents.get('contactsPhone', '+7 (911) 999-99-99')
            context['contacts_email'] = contacts_contents.get('contactsEmail', 'example@example.ru')

            # Социальные сети
            context['contacts_vk'] = contacts_contents.get('contactsVK', 'https://vk.com/id39146412')
            context['contacts_whatsapp'] = contacts_contents.get('contactsWhatsApp', 'https://wa.me/79111292655')
            context['contacts_telegram'] = contacts_contents.get('contactsTelegramm', 'https://t.me/Elen0Fil')

            # Логирование координат для отладки
            logger.debug(f"Координаты из базы данных: Широта={context['contacts_latitude']}, " +
                         f"Долгота={context['contacts_longitude']}")

        else:
            # Безопасные значения по умолчанию для контактов
            context['contacts_city'] = 'Санкт-Петербург'
            context['contacts_address'] = 'ул. Среднерогатская'
            context['contacts_latitude'] = '59.819987'      # Для работы карты
            context['contacts_longitude'] = '30.337649'     # Для работы карты
            context['contacts_phone'] = '+7 (911) 999-99-99'
            context['contacts_email'] = 'example@example.ru'
            context['contacts_vk'] = 'https://vk.com/id39146412'
            context['contacts_whatsapp'] = 'https://wa.me/79111292655'
            context['contacts_telegram'] = 'https://t.me/Elen0Fil'

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
        context['contacts_city'] = 'Санкт-Петербург'

        # Координаты для карты
        context['contacts_latitude'] = '59.819987'
        context['contacts_longitude'] = '30.337649'

        logger.warning("Используется резервный режим с безопасными значениями")

    return render(request, 'index.html', context)


def privacy(request):
    """
    Обработчик для страницы политики конфиденциальности
    Простая статическая страница без динамического контента
    """
    return render(request, 'privacy.html')