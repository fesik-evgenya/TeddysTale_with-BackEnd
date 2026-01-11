// Cookie Consent Management
document.addEventListener('DOMContentLoaded', function() {
    const cookieModal = document.getElementById('cookieConsentModal');
    const acceptBtn = document.getElementById('acceptCookies');
    const declineBtn = document.getElementById('declineCookies');

    // Функция для плавного скрытия модального окна
    function hideCookieModal() {
        if (cookieModal) {
            cookieModal.classList.add('hiding');
            setTimeout(() => {
                cookieModal.style.display = 'none';
                cookieModal.classList.remove('hiding');
            }, 300);
        }
    }

    // Проверяем, было ли уже дано согласие (сохранено в localStorage)
    const hasConsent = localStorage.getItem('teddyTaleCookieConsent');

    if (!hasConsent) {
        // Показываем модальное окно через 1 секунду после загрузки
        setTimeout(() => {
            if (cookieModal) {
                cookieModal.style.display = 'flex';
            }
        }, 1000);
    }

    // Обработчик принятия cookie
    if (acceptBtn) {
        acceptBtn.addEventListener('click', function() {
            localStorage.setItem('teddyTaleCookieConsent', 'accepted');
            localStorage.setItem('teddyTaleCookieConsentDate', new Date().toISOString());

            hideCookieModal();

            console.log('Cookie согласие принято - TeddyTale');

            // Показать подтверждение (опционально)
            showAcceptanceMessage();
        });
    }

    // Обработчик отказа от cookie
    if (declineBtn) {
        declineBtn.addEventListener('click', function() {
            localStorage.setItem('teddyTaleCookieConsent', 'declined');
            localStorage.setItem('teddyTaleCookieConsentDate', new Date().toISOString());

            hideCookieModal();

            // Удаляем все cookies, которые мы могли установить
            clearCookies();

            console.log('Cookie согласие отклонено - TeddyTale');
        });
    }

    // Функция для очистки cookies
    function clearCookies() {
        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i];
            const eqPos = cookie.indexOf("=");
            const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();

            // Удаляем cookie, устанавливая дату истечения в прошлое
            document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        }
    }

    // Функция для показа сообщения о принятии (опционально)
    function showAcceptanceMessage() {
        const message = document.createElement('div');
        message.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, var(--color-pink) 0%, var(--color-lavender) 100%);
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                box-shadow: var(--shadow-lg);
                z-index: 10000;
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
                animation: slideInRight 0.3s ease-out;
                border: 1px solid rgba(255, 255, 255, 0.2);
                max-width: 300px;
            ">
                Спасибо! Ваши настройки cookie сохранены.
            </div>
        `;

        document.body.appendChild(message);

        // Удаляем сообщение через 3 секунды
        setTimeout(() => {
            message.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 300);
        }, 3000);
    }

    // Убрали закрытие при клике вне модального окна
    // Теперь пользователь должен обязательно нажать одну из кнопок

    // Добавляем стили для анимации сообщения
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});