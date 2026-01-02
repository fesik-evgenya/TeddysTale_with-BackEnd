// map.js - упрощенная версия

document.addEventListener('DOMContentLoaded', function () {
    const mapElement = document.getElementById('map');

    if (!mapElement) {
        console.error('Элемент карты не найден');
        return;
    }

    // Получаем координаты из глобальной переменной mapData (из шаблона Django)
    let latitude, longitude;

    // Проверяем наличие глобальной переменной mapData из шаблона
    if (window.mapData && window.mapData.latitude && window.mapData.longitude) {
        latitude = parseFloat(window.mapData.latitude);
        longitude = parseFloat(window.mapData.longitude);
        console.log('Карта: координаты из mapData', latitude, longitude);
    }
    // Если нет mapData, проверяем старые глобальные переменные
    else if (window.contacts_latitude && window.contacts_longitude) {
        latitude = parseFloat(window.contacts_latitude);
        longitude = parseFloat(window.contacts_longitude);
        console.log('Карта: координаты из window переменных', latitude, longitude);
    }
    // Если нет глобальных переменных, проверяем data-атрибуты
    else {
        const dataLatitude = mapElement.getAttribute('data-latitude');
        const dataLongitude = mapElement.getAttribute('data-longitude');

        if (dataLatitude && dataLongitude) {
            latitude = parseFloat(dataLatitude);
            longitude = parseFloat(dataLongitude);
            console.log('Карта: координаты из data-атрибутов', latitude, longitude);
        } else {
            // Резервные координаты (Санкт-Петербург)
            latitude = 59.819987;
            longitude = 30.337649;
            console.log('Карта: использованы резервные координаты');
        }
    }

    // Проверяем валидность координат
    if (isNaN(latitude) || isNaN(longitude)) {
        console.error('Некорректные координаты, используем резервные');
        latitude = 59.819987;
        longitude = 30.337649;
    }

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