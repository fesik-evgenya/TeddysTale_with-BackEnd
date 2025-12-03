/**
 * Функция для плавной прокрутки к выбранному слоту товара
 * @param {string} slotId - ID элемента, к которому нужно прокрутить
 */
function scrollToSlot(slotId) {
    // Проверяем, что выбран действительный слот (не пустое значение)
    if (!slotId) return;

    // Находим целевой элемент по ID
    const targetElement = document.getElementById(slotId);

    if (targetElement) {
        // Получаем высоту фиксированного хедера
        const header = document.querySelector('header');
        const headerHeight = header ? header.offsetHeight : 0;

        // Добавляем дополнительный отступ для комфортного просмотра
        const additionalOffset = 100;
        const totalOffset = headerHeight + additionalOffset;

        // Вычисляем позицию элемента с учетом отступа (используем современный scrollY)
        const elementPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.scrollY - totalOffset;

        // Выполняем плавную прокрутку
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });

        // Добавляем визуальный акцент на выбранный элемент
        highlightSelectedCard(targetElement);
    } else {
        console.warn(`Элемент с ID "${slotId}" не найден`);
    }
}

/**
 * Функция для подсветки выбранной карточки товара
 * @param {HTMLElement} element - Выбранный элемент карточки
 */
function highlightSelectedCard(element) {
    // Убираем подсветку со всех карточек
    const allCards = document.querySelectorAll('.card');
    allCards.forEach(card => {
        card.style.boxShadow = '';
        card.style.transition = 'box-shadow 0.3s ease';
    });

    // Добавляем подсветку к выбранной карточке
    element.style.boxShadow = '0 0 0 3px var(--color-pink), 0 8px 25px rgba(232, 180, 184, 0.4)';

    // Убираем подсветку через 2 секунды
    setTimeout(() => {
        element.style.boxShadow = '';
    }, 2000);
}

/**
 * Функция для закрытия мобильного меню
 */
function closeMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const mobileMenu = document.querySelector('.mobile-menu');
    const body = document.body;

    hamburger.classList.remove('active');
    mobileMenu.classList.remove('active');
    body.classList.remove('menu-open');
}

/**
 * Функция для инициализации мобильного меню
 */
function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const mobileMenu = document.querySelector('.mobile-menu');
    const body = document.body;

    // Если элементов мобильного меню нет на странице - выходим
    if (!hamburger || !mobileMenu) return;

    // Открытие/закрытие меню по клику на бургер
    hamburger.addEventListener('click', function(e) {
        e.stopPropagation();
        this.classList.toggle('active');
        mobileMenu.classList.toggle('active');
        body.classList.toggle('menu-open');
    });

    // Закрытие по клику на ссылку в мобильном меню
    mobileMenu.querySelectorAll('.header-navigation a').forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });

    // Закрытие по клику на крестик
    const closeBtn = document.querySelector('.close-mobile-menu');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeMobileMenu);
    }

    // Закрытие по клику вне меню
    document.addEventListener('click', function(e) {
        if (mobileMenu.classList.contains('active') &&
            !mobileMenu.contains(e.target) &&
            !hamburger.contains(e.target)) {
            closeMobileMenu();
        }
    });

    // Закрытие при ресайзе на десктоп
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    });

    // Закрытие по нажатию Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
            closeMobileMenu();
        }
    });
}

/**
 * Функция для инициализации обработчиков событий после загрузки DOM
 */
function initAdminPanel() {
    // Добавляем обработчик изменения выпадающего списка
    const slotSelector = document.getElementById('slotSelector');
    if (slotSelector) {
        slotSelector.addEventListener('change', function() {
            scrollToSlot(this.value);
        });
    }

    // Добавляем обработчики для навигации по якорным ссылкам в хедере
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            scrollToSlot(targetId);
        });
    });

    // Инициализируем мобильное меню
    initMobileMenu();

    console.log('Admin Panel navigation and mobile menu initialized successfully');
}

// Унифицированная инициализация для всех случаев загрузки DOM
function initialize() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAdminPanel);
    } else {
        initAdminPanel();
    }
}

// Запускаем инициализацию
initialize();