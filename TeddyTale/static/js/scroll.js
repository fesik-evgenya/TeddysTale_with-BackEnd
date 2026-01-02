// ===== ПЛАВНЫЙ СКРОЛЛ ДО ЯКОРНЫХ ССЫЛОК =====
// Оптимизирован с учетом высоты фиксированного хедера и UX/UI практик

document.addEventListener('DOMContentLoaded', function() {
    // Получаем текущую высоту хедера с учетом всех стилей и медиазапросов
    const getHeaderHeight = () => {
        const header = document.querySelector('header');
        if (!header) return 80; // Значение по умолчанию для десктопа

        // Используем getComputedStyle для получения актуальных CSS-свойств
        const computedStyle = window.getComputedStyle(header);

        // Приоритет: height -> min-height -> offsetHeight
        let height = parseInt(computedStyle.height) ||
            parseInt(computedStyle.minHeight) ||
            header.offsetHeight;

        // Добавляем небольшой визуальный отступ для лучшего восприятия
        // (позволяет видеть начало секции с небольшим контекстом)
        const visualOffset = 15;

        return Math.max(height + visualOffset, 80); // Минимум 80px
    };

    // Функция для плавного скролла к элементу
    const scrollToElement = (element, duration = 600) => {
        if (!element) return;

        const headerHeight = getHeaderHeight();
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - headerHeight;

        // Отменяем любой активный скролл
        if (window.currentScrollAnimation) {
            window.cancelAnimationFrame(window.currentScrollAnimation);
        }

        // Анимация скролла с easing функцией
        const startPosition = window.pageYOffset;
        const distance = offsetPosition - startPosition;
        const startTime = performance.now();

        const easeInOutQuad = (t) => {
            return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        };

        const animateScroll = (currentTime) => {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            const easeProgress = easeInOutQuad(progress);

            window.scrollTo(0, startPosition + distance * easeProgress);

            if (progress < 1) {
                window.currentScrollAnimation = requestAnimationFrame(animateScroll);
            } else {
                window.currentScrollAnimation = null;

                // Обновляем URL в браузере без перезагрузки страницы
                const targetId = element.getAttribute('id');
                if (targetId && history.pushState) {
                    history.pushState(null, null, `#${targetId}`);
                }
            }
        };

        window.currentScrollAnimation = requestAnimationFrame(animateScroll);
    };

    // Закрытие мобильного меню при клике на якорную ссылку
    const closeMobileMenu = () => {
        const mobileMenu = document.querySelector('.mobile-menu');
        const hamburger = document.querySelector('.hamburger');

        if (mobileMenu && mobileMenu.classList.contains('active')) {
            mobileMenu.classList.remove('active');
            hamburger?.classList.remove('active');
            document.body.classList.remove('menu-open');
        }
    };

    // Обработка всех якорных ссылок на странице
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Игнорируем пустые ссылки
            if (href === '#' || href === '#!') return;

            // Для якорных ссылок на текущей странице
            if (href.startsWith('#')) {
                e.preventDefault();

                const targetElement = document.querySelector(href);
                if (!targetElement) return;

                // Закрываем мобильное меню
                closeMobileMenu();

                // Плавный скролл к цели
                scrollToElement(targetElement);

                // Фокусировка на элементе для доступности
                setTimeout(() => {
                    targetElement.setAttribute('tabindex', '-1');
                    targetElement.focus({ preventScroll: true });
                    targetElement.removeAttribute('tabindex');
                }, 100);
            }
        });
    });

    // Обработка прямого перехода по URL с якорем (при загрузке страницы)
    const handleInitialHash = () => {
        if (window.location.hash) {
            const targetElement = document.querySelector(window.location.hash);
            if (targetElement) {
                // Небольшая задержка для полной загрузки страницы
                setTimeout(() => {
                    scrollToElement(targetElement, 400);
                }, 100);
            }
        }
    };

    // Обработка изменения хэша в URL (навигация в истории браузера)
    window.addEventListener('hashchange', () => {
        if (window.location.hash) {
            const targetElement = document.querySelector(window.location.hash);
            if (targetElement) {
                scrollToElement(targetElement);
            }
        }
    });

    // Адаптация к изменению размера окна
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            // Если есть активный якорь в URL, корректируем позицию
            if (window.location.hash) {
                const targetElement = document.querySelector(window.location.hash);
                if (targetElement) {
                    const headerHeight = getHeaderHeight();
                    const elementPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
                    const offsetPosition = elementPosition - headerHeight;

                    // Мгновенная коррекция без анимации
                    window.scrollTo(0, offsetPosition);
                }
            }
        }, 150);
    });

    // Инициализация при загрузке
    handleInitialHash();

    // Добавляем обработчик для кнопок с классом .btn-card и .btn-about
    // которые могут быть нестандартными ссылками
    document.querySelectorAll('.btn-card, .btn-about, .placeholder-card__button').forEach(button => {
        if (button.tagName === 'A' && button.getAttribute('href')?.startsWith('#')) {
            // Для ссылок уже есть обработчик выше
            return;
        }

        if (button.hasAttribute('data-target')) {
            button.addEventListener('click', () => {
                const targetId = button.getAttribute('data-target');
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    closeMobileMenu();
                    scrollToElement(targetElement);
                }
            });
        }
    });
});

// Дополнительная функция для программного скролла (можно вызывать из других скриптов)
window.scrollToSection = function(sectionId, duration = 600) {
    const targetElement = document.querySelector(sectionId);
    if (targetElement) {
        const header = document.querySelector('header');
        const headerHeight = header ? header.offsetHeight + 15 : 80;
        const elementPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - headerHeight;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });

        // Обновляем URL
        if (history.pushState) {
            history.pushState(null, null, sectionId);
        }

        return true;
    }
    return false;
};