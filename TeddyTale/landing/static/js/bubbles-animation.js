(function() {
    'use strict';

    // Конфигурация анимации (в 5 раз медленнее)
    const CONFIG = {
        maxSpeed: 0.06,        // Основная скорость движения
        driftSpeed: 0.0002,    // Скорость изменения направления
        amplitude: 15,         // Амплитуда колебаний
        frequency: 0.0004,     // Частота колебаний
        updateInterval: 30,    // Интервал обновления
        margin: 50             // Отступ от краев
    };

    let animationId = null;
    let lastUpdateTime = 0;
    let isMobile = window.innerWidth <= 768;
    let ellipses = [];
    let mainElement = null;

    // Получение размеров области движения (только внутри main)
    function getMovementArea() {
        if (!mainElement) {
            mainElement = document.querySelector('main');
            if (!mainElement) {
                return {
                    minX: 0,
                    maxX: window.innerWidth,
                    minY: 0,
                    maxY: window.innerHeight,
                    width: window.innerWidth,
                    height: window.innerHeight
                };
            }
        }

        const mainRect = mainElement.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

        return {
            minX: mainRect.left + scrollLeft,
            maxX: mainRect.right + scrollLeft,
            minY: mainRect.top + scrollTop,
            maxY: mainRect.bottom + scrollTop,
            width: mainRect.width,
            height: mainRect.height
        };
    }

    // Инициализация эллипсов
    function initEllipses() {
        const selectors = [
            '.ellipses-small-hero', '.ellipses-middle-hero', '.ellipses-big-hero',
            '.ellipses-small-about', '.ellipses-middle-about', '.ellipses-big-about',
            '.ellipses-small-contacts', '.ellipses-middle-contacts', '.ellipses-big-contacts'
        ];

        const area = getMovementArea();

        ellipses = selectors.map(selector => {
            const element = document.querySelector(selector);
            if (!element) return null;

            // Случайная начальная позиция внутри main
            const startX = Math.random() * (area.width - 100) + area.minX + 50;
            const startY = Math.random() * (area.height - 100) + area.minY + 50;

            // Случайные начальные параметры движения
            return {
                element,
                x: startX,
                y: startY,
                vx: (Math.random() - 0.5) * CONFIG.maxSpeed,
                vy: (Math.random() - 0.5) * CONFIG.maxSpeed,
                driftX: (Math.random() - 0.5) * CONFIG.driftSpeed,
                driftY: (Math.random() - 0.5) * CONFIG.driftSpeed,
                timeOffset: Math.random() * Math.PI * 2,
                amplitude: CONFIG.amplitude * (0.5 + Math.random() * 0.5),
                frequency: CONFIG.frequency * (0.8 + Math.random() * 0.4),
                elementWidth: 0,
                elementHeight: 0
            };
        }).filter(Boolean);

        // Устанавливаем начальные позиции и получаем размеры элементов
        ellipses.forEach(ellipse => {
            const rect = ellipse.element.getBoundingClientRect();
            ellipse.elementWidth = rect.width;
            ellipse.elementHeight = rect.height;

            ellipse.element.style.left = `${ellipse.x}px`;
            ellipse.element.style.top = `${ellipse.y}px`;
        });
    }

    // Плавное изменение направления при приближении к границам
    function applyBoundarySteering(ellipse, area) {
        const boundaryMargin = CONFIG.margin;
        const steerStrength = 0.0005;

        // Определяем расстояние до границ main
        const leftDist = ellipse.x - area.minX;
        const rightDist = area.maxX - ellipse.x - ellipse.elementWidth;
        const topDist = ellipse.y - area.minY;
        const bottomDist = area.maxY - ellipse.y - ellipse.elementHeight;

        // Плавно меняем направление при приближении к границам main
        if (leftDist < boundaryMargin) {
            ellipse.vx += steerStrength * (boundaryMargin - leftDist);
        } else if (rightDist < boundaryMargin) {
            ellipse.vx -= steerStrength * (boundaryMargin - rightDist);
        }

        if (topDist < boundaryMargin) {
            ellipse.vy += steerStrength * (boundaryMargin - topDist);
        } else if (bottomDist < boundaryMargin) {
            ellipse.vy -= steerStrength * (boundaryMargin - bottomDist);
        }
    }

    // Обновление позиции одного эллипса
    function updateEllipse(ellipse, deltaTime) {
        const area = getMovementArea();

        // Обновляем скорость с небольшим дрейфом
        ellipse.vx += ellipse.driftX * deltaTime;
        ellipse.vy += ellipse.driftY * deltaTime;

        // Применяем плавное управление у границ
        applyBoundarySteering(ellipse, area);

        // Ограничиваем максимальную скорость
        const speed = Math.sqrt(ellipse.vx * ellipse.vx + ellipse.vy * ellipse.vy);
        if (speed > CONFIG.maxSpeed) {
            ellipse.vx = (ellipse.vx / speed) * CONFIG.maxSpeed;
            ellipse.vy = (ellipse.vy / speed) * CONFIG.maxSpeed;
        }

        // Добавляем синусоидальное движение для естественности
        const time = Date.now() * 0.001;
        const sineX = Math.sin(time * ellipse.frequency + ellipse.timeOffset) * ellipse.amplitude;
        const sineY = Math.cos(time * ellipse.frequency + ellipse.timeOffset * 1.3) * ellipse.amplitude;

        // Обновляем позицию
        ellipse.x += ellipse.vx * deltaTime + sineX * 0.01;
        ellipse.y += ellipse.vy * deltaTime + sineY * 0.01;

        // Жесткие границы с отражением (только внутри main)
        if (ellipse.x < area.minX) {
            ellipse.x = area.minX;
            ellipse.vx = Math.abs(ellipse.vx) * 0.8;
        } else if (ellipse.x + ellipse.elementWidth > area.maxX) {
            ellipse.x = area.maxX - ellipse.elementWidth;
            ellipse.vx = -Math.abs(ellipse.vx) * 0.8;
        }

        if (ellipse.y < area.minY) {
            ellipse.y = area.minY;
            ellipse.vy = Math.abs(ellipse.vy) * 0.8;
        } else if (ellipse.y + ellipse.elementHeight > area.maxY) {
            ellipse.y = area.maxY - ellipse.elementHeight;
            ellipse.vy = -Math.abs(ellipse.vy) * 0.8;
        }

        // Применяем новую позицию
        ellipse.element.style.left = `${ellipse.x}px`;
        ellipse.element.style.top = `${ellipse.y}px`;
    }

    // Основной цикл анимации
    function animate(currentTime) {
        if (!lastUpdateTime) lastUpdateTime = currentTime;

        const deltaTime = Math.min(currentTime - lastUpdateTime, 50);

        if (deltaTime >= CONFIG.updateInterval) {
            ellipses.forEach(ellipse => updateEllipse(ellipse, deltaTime));
            lastUpdateTime = currentTime;
        }

        animationId = requestAnimationFrame(animate);
    }

    // Запуск анимации
    function startAnimation() {
        if (isMobile || ellipses.length === 0 || animationId) return;

        lastUpdateTime = 0;
        animationId = requestAnimationFrame(animate);
    }

    // Остановка анимации
    function stopAnimation() {
        if (animationId) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
    }

    // Обработчик изменения размера окна и скролла
    function handleResize() {
        const wasMobile = isMobile;
        isMobile = window.innerWidth <= 768;

        if (wasMobile && !isMobile) {
            // Переход с мобильного на десктоп
            mainElement = document.querySelector('main');
            initEllipses();
            startAnimation();
        } else if (!wasMobile && isMobile) {
            // Переход с десктопа на мобильный
            stopAnimation();
        } else if (!isMobile) {
            // Просто изменился размер десктопного окна - обновляем размеры элементов
            mainElement = document.querySelector('main');
            ellipses.forEach(ellipse => {
                const rect = ellipse.element.getBoundingClientRect();
                ellipse.elementWidth = rect.width;
                ellipse.elementHeight = rect.height;
            });
        }
    }

    // Инициализация при загрузке
    function init() {
        if (!isMobile) {
            mainElement = document.querySelector('main');
            initEllipses();
            startAnimation();
        }

        // Добавляем обработчики событий
        window.addEventListener('resize', handleResize);
        window.addEventListener('orientationchange', handleResize);
        window.addEventListener('scroll', handleResize); // Обновляем при скролле
    }

    // Запускаем когда DOM готов
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Очистка при выгрузке страницы
    window.addEventListener('beforeunload', () => {
        stopAnimation();
        window.removeEventListener('resize', handleResize);
        window.removeEventListener('orientationchange', handleResize);
        window.removeEventListener('scroll', handleResize);
    });
})();