document.addEventListener('DOMContentLoaded', () => {
    const formInputs = document.querySelectorAll('.form input[type="text"], .form input[type="email"], .form input[type="password"], .form textarea');

    formInputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.style.transform = 'scale(1.02)';
        });

        input.addEventListener('blur', () => {
            input.style.transform = 'scale(1)';
        });
    });
});