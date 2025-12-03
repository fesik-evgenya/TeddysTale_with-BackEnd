// Плавный скролл с учетом высоты хедера
document.addEventListener('DOMContentLoaded', function() {
    const header = document.querySelector('header');
    const headerHeight = header ? header.offsetHeight : 0;
    const offset = headerHeight; // 100px хедер

    // Обработка кликов по ссылкам с якорями
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - offset;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
});