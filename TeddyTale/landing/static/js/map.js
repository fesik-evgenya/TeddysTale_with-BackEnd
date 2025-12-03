/**
 * Инициализация Яндекс.Карты с логотипом
 * @param {Array} center - Координаты центра [широта, долгота]
 * @param {number} zoom - Уровень масштабирования
 * @param {string} elementId - ID контейнера для карты
 */
function initMap(center = [59.819987, 30.337649], zoom = 13, elementId = 'map') {
    if (typeof ymaps === 'undefined') {
        console.error('Yandex Maps API не загружен');
        return;
    }

    // Проверяем, существует ли элемент с таким ID
    const container = document.getElementById(elementId);
    if (!container) {
        console.error(`Контейнер для карты с id="${elementId}" не найден`);
        return;
    }

    ymaps.ready(() => {
        const myMap = new ymaps.Map(elementId, {
            center: center,
            zoom: zoom,
            controls: ['zoomControl']
        });

        // Путь к логотипу
        const logoPath = './assets/icon/teedy-logo.svg';

        // Размеры метки
        const iconSize = [30, 30];
        const iconOffset = [-15, -15];

        // Создание кастомной метки
        const myPlacemark = new ymaps.Placemark(
            center,
            {},
            {
                iconLayout: 'default#image',
                iconImageHref: logoPath,
                iconImageSize: iconSize,
                iconImageOffset: iconOffset,
                iconShape: {
                    type: 'Circle',
                    coordinates: [0, 0],
                    radius: 15
                }
            }
        );

        myMap.geoObjects.add(myPlacemark);

        // Анимация пульсации
        let isLarge = false;
        setInterval(() => {
            isLarge = !isLarge;
            const size = isLarge ? [28, 30] : [30, 32];
            myPlacemark.options.set('iconImageSize', size);
        }, 450);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    initMap();
});