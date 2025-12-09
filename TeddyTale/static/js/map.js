// map.js - упрощенная версия

document.addEventListener('DOMContentLoaded', function () {
    const mapElement = document.getElementById('map');

    if (!mapElement) {
        console.error('Элемент карты не найден');
        return;
    }

    // Получаем координаты из data-атрибутов или используем значения по умолчанию
    const latitude = mapElement.getAttribute('data-latitude') ||
        window.contacts_latitude ||
        59.819987;

    const longitude = mapElement.getAttribute('data-longitude') ||
        window.contacts_longitude ||
        30.337649;

    const logoPath = mapElement.getAttribute('data-logo-path') ||
        '/static/assets/icon/teedy-logo.svg';

    // Инициализируем карту
    initYandexMap(latitude, longitude, logoPath);
});

function initYandexMap(latitude, longitude, logoPath) {
    if (typeof ymaps === 'undefined') {
        console.error('Yandex Maps API не загружен');
        return;
    }

    ymaps.ready(function() {
        const map = new ymaps.Map('map', {
            center: [latitude, longitude],
            zoom: 13,
            controls: ['zoomControl']
        });

        const placemark = new ymaps.Placemark([latitude, longitude], {}, {
            iconLayout: 'default#image',
            iconImageHref: logoPath,
            iconImageSize: [30, 30],
            iconImageOffset: [-15, -15]
        });

        map.geoObjects.add(placemark);

        // Анимация пульсации
        let isLarge = false;
        setInterval(() => {
            isLarge = !isLarge;
            placemark.options.set('iconImageSize', isLarge ? [28, 30] : [30, 32]);
        }, 450);
    });
}