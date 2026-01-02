/**
 * admin-panel.js - JavaScript для кастомной админ-панели Teddy's Tale
 */

/**
 * Функция для получения значения cookie по имени (исправленная версия)
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Проверяем, начинается ли cookie с нужного имени
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Функция для получения CSRF токена (универсальная)
 */
function getCSRFToken() {
    // Сначала пытаемся получить из мета-тега
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }

    // Затем пытаемся получить из скрытого поля
    const hiddenToken = document.querySelector('[name="csrfmiddlewaretoken"]');
    if (hiddenToken) {
        return hiddenToken.value;
    }

    // Пытаемся получить из куки
    const cookieToken = getCookie('csrftoken');
    if (cookieToken) {
        return cookieToken;
    }

    console.warn('CSRF token not found. AJAX requests may fail.');
    return '';
}

/**
 * Функция для плавной прокрутки к выбранному слоту товара
 * @param {string} slotId - ID элемента, к которому нужно прокрутить
 */
function scrollToSlot(slotId) {
    if (!slotId) return;
    const targetElement = document.getElementById(slotId);
    if (targetElement) {
        const header = document.querySelector('header');
        const headerHeight = header ? header.offsetHeight : 0;
        const additionalOffset = 100;
        const totalOffset = headerHeight + additionalOffset;
        const elementPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.scrollY - totalOffset;
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
        highlightSelectedCard(targetElement);
    } else {
        console.warn(`Элемент с ID "${slotId}" не найден`);
    }
}

/**
 * Функция для подсветки выбранной карточки товара
 */
function highlightSelectedCard(element) {
    const allCards = document.querySelectorAll('.card');
    allCards.forEach(card => {
        card.style.boxShadow = '';
        card.style.transition = 'box-shadow 0.3s ease';
    });
    element.style.boxShadow = '0 0 0 3px var(--color-pink), 0 8px 25px rgba(232, 180, 184, 0.4)';
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
    if (!hamburger || !mobileMenu) return;
    hamburger.addEventListener('click', function(e) {
        e.stopPropagation();
        this.classList.toggle('active');
        mobileMenu.classList.toggle('active');
        body.classList.toggle('menu-open');
    });
    mobileMenu.querySelectorAll('.header-navigation a').forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });
    const closeBtn = document.querySelector('.close-mobile-menu');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeMobileMenu);
    }
    document.addEventListener('click', function(e) {
        if (mobileMenu.classList.contains('active') &&
            !mobileMenu.contains(e.target) &&
            !hamburger.contains(e.target)) {
            closeMobileMenu();
        }
    });
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
            closeMobileMenu();
        }
    });
}

/**
 * Функция показа уведомлений
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        z-index: 1000;
        font-weight: bold;
        animation: slideIn 0.3s ease-out;
    `;
    if (type === 'success') {
        notification.style.backgroundColor = '#4CAF50';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#F44336';
    } else {
        notification.style.backgroundColor = '#2196F3';
    }
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Общая функция для выполнения AJAX запросов (исправленная версия)
 */
async function sendAjaxRequest(url, method = 'POST', data = null) {
    const csrfToken = getCSRFToken();

    const headers = {
        'X-CSRFToken': csrfToken,
    };

    let body = data;

    // Если data - объект FormData, не устанавливаем Content-Type
    // Если data - объект, преобразуем в JSON
    if (data && !(data instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: headers,
            body: body,
            credentials: 'same-origin'  // Важно для отправки кук
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const responseData = await response.json();
        return responseData;
    } catch (error) {
        console.error('AJAX request failed:', error);
        throw error;
    }
}

/**
 * Обработчик для форм редактирования секций
 */
function initSectionForms() {
    document.querySelectorAll('.form-fields[data-section]').forEach(form => {
        // Пропускаем форму contacts-point, у нее особая обработка
        if (form.id === 'contacts-point') return;

        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const section = this.dataset.section;
            const contentKey = this.dataset.contentKey || this.id.replace('adminPanel-', '');
            let value = '';

            // Получаем значение из формы
            const input = this.querySelector('input, textarea, select');
            if (input) {
                value = input.type === 'checkbox' ? input.checked : input.value;
            }

            try {
                const data = await sendAjaxRequest(
                    `/admin-custom/ajax/update-section/${section}/`, // ИСПРАВЛЕННЫЙ URL
                    'POST',
                    {
                        content_key: contentKey,
                        value: value,
                        label: this.querySelector('label')?.textContent || contentKey,
                    }
                );

                if (data.status === 'success') {
                    showNotification('Успешно сохранено!', 'success');
                } else {
                    showNotification(data.message || 'Ошибка сохранения', 'error');
                }
            } catch (error) {
                showNotification('Ошибка при сохранении', 'error');
            }
        });
    });
}

/**
 * Обработчик для формы координат (особый случай) - ИСПРАВЛЕННАЯ ВЕРСИЯ
 */
function initContactsPointForm() {
    const contactsPointForm = document.getElementById('contacts-point');
    if (!contactsPointForm) return;

    contactsPointForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const latitudeInput = this.querySelector('#contactsPoints_latitude');
        const longitudeInput = this.querySelector('#contactsPoints_longitude');

        if (!latitudeInput || !longitudeInput) return;

        try {
            // ПРАВИЛЬНЫЙ URL согласно структуре urls.py
            const baseUrl = '/admin-custom/ajax/update-section/contacts/';

            // Сохраняем широту
            const latData = await sendAjaxRequest(
                baseUrl,
                'POST',
                {
                    content_key: 'contactsPoints_latitude',
                    value: latitudeInput.value,
                    label: 'Широта',
                }
            );

            if (latData.status !== 'success') {
                throw new Error(latData.message || 'Ошибка сохранения широты');
            }

            // Сохраняем долготу
            const lonData = await sendAjaxRequest(
                baseUrl,
                'POST',
                {
                    content_key: 'contactsPoints_longitude',
                    value: longitudeInput.value,
                    label: 'Долгота',
                }
            );

            if (lonData.status === 'success') {
                showNotification('Координаты сохранены!', 'success');
            } else {
                showNotification(lonData.message || 'Ошибка сохранения долготы', 'error');
            }
        } catch (error) {
            console.error('Error in contacts form:', error);
            showNotification(error.message || 'Ошибка при сохранении координат', 'error');
        }
    });
}

/**
 * Обработчик для форм редактирования товаров
 */
function initShopItemForms() {
    document.querySelectorAll('.form-fields[data-item-id]').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const itemId = this.dataset.itemId;
            const field = this.dataset.field;
            const input = this.querySelector('input, textarea');

            if (!input) return;

            try {
                const data = await sendAjaxRequest(
                    `/admin-custom/ajax/update-shop-item/${itemId}/`,
                    'POST',
                    {
                        [field]: input.value
                    }
                );

                if (data.status === 'success') {
                    showNotification('Товар обновлен!', 'success');
                } else {
                    showNotification(data.message || 'Ошибка обновления', 'error');
                }
            } catch (error) {
                showNotification('Ошибка при обновлении товара', 'error');
            }
        });
    });
}

/**
 * Обработчик для загрузки изображений секций (hero, about, etc.)
 */
function initImageUploadForms() {
    document.querySelectorAll('.upload-submit-button').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();

            const form = this.closest('form');
            if (!form) return;

            const fileInput = form.querySelector('input[type="file"]');
            const sectionType = form.dataset.section || '';
            const contentKey = form.dataset.contentKey || '';

            // Проверяем, это форма товара или секции
            const isShopItemForm = form.dataset.itemId && form.dataset.field === 'image';
            if (isShopItemForm) {
                // Пропускаем формы товаров, у них своя обработка
                return;
            }

            if (!fileInput || fileInput.files.length === 0) {
                showNotification('Выберите файл для загрузки', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            formData.append('section_type', sectionType);
            formData.append('content_key', contentKey);

            try {
                const data = await sendAjaxRequest(
                    '/admin-custom/ajax/upload-image/',
                    'POST',
                    formData
                );

                if (data.status === 'success') {
                    showNotification('Изображение загружено!', 'success');

                    // Обновляем изображение на странице
                    const img = form.querySelector('img');
                    if (img && data.data && data.data.url) {
                        img.src = data.data.url;
                        img.alt = 'Загруженное изображение';
                    }

                    // Обновляем имя файла
                    const fileNameSpan = form.querySelector('.image-set_name, .upload-controls > span');
                    if (fileNameSpan && data.data && data.data.stored_filename) {
                        fileNameSpan.textContent = data.data.stored_filename;
                    }
                } else {
                    showNotification(data.message || 'Ошибка загрузки', 'error');
                }
            } catch (error) {
                showNotification('Ошибка при загрузке изображения', 'error');
            }
        });
    });
}

/**
 * Обработчик для загрузки изображений товаров
 */
function initShopItemImageUploadForms() {
    document.querySelectorAll('.form-fields[data-item-id][data-field="image"] .upload-submit-button').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();

            const form = this.closest('form');
            if (!form) return;

            const fileInput = form.querySelector('input[type="file"]');
            const itemId = form.dataset.itemId;

            if (!fileInput || fileInput.files.length === 0) {
                showNotification('Выберите файл для загрузки', 'error');
                return;
            }

            if (!itemId) {
                showNotification('Ошибка: ID товара не найден', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('image', fileInput.files[0]);

            try {
                const data = await sendAjaxRequest(
                    `/admin-custom/ajax/upload-shop-item-image/${itemId}/`,
                    'POST',
                    formData
                );

                if (data.status === 'success') {
                    showNotification('Изображение товара загружено!', 'success');

                    // Обновляем изображение на странице
                    const img = form.querySelector('img');
                    if (img && data.data && data.data.image_url) {
                        img.src = data.data.image_url;
                        img.alt = 'Загруженное изображение товара';
                    }

                    // Обновляем имя файла
                    const fileNameSpan = form.querySelector('.image-set_name, .upload-controls > span');
                    if (fileNameSpan && data.data && data.data.image_name) {
                        fileNameSpan.textContent = data.data.image_name;
                    }
                } else {
                    showNotification(data.message || 'Ошибка загрузки изображения товара', 'error');
                }
            } catch (error) {
                showNotification('Ошибка при загрузке изображения товара', 'error');
            }
        });
    });
}

/**
 * Инициализация селектора слотов
 */
function initSlotSelector() {
    const slotSelector = document.getElementById('slotSelector');
    if (!slotSelector) return;

    slotSelector.addEventListener('change', function() {
        if (this.value) {
            scrollToSlot(this.value);
        }
    });
}

/**
 * Инициализация навигации по якорным ссылкам
 */
function initAnchorNavigation() {
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            scrollToSlot(targetId);
        });
    });
}

/**
 * Основная функция инициализации
 */
function initAdminPanel() {
    console.log('Инициализация админ-панели...');

    // Инициализация элементов интерфейса
    initSlotSelector();
    initAnchorNavigation();
    initMobileMenu();

    // Инициализация форм
    initSectionForms();
    initContactsPointForm();
    initShopItemForms();
    initImageUploadForms();
    initShopItemImageUploadForms();  // Добавлена новая функция

    console.log('Админ-панель успешно инициализирована');
}

/**
 * Вспомогательная функция для инициализации при загрузке DOM
 */
function initialize() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAdminPanel);
    } else {
        // DOM уже загружен
        initAdminPanel();
    }
}

// Запуск инициализации
initialize();

// Экспорт функций для глобального доступа (если нужно)
window.scrollToSlot = scrollToSlot;
window.showNotification = showNotification;
window.getCSRFToken = getCSRFToken;
window.sendAjaxRequest = sendAjaxRequest;