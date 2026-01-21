document.addEventListener('DOMContentLoaded', () => {
    const themeToggles = document.querySelectorAll('.theme-toggle');
    const currentTheme = localStorage.getItem('theme');
    const year = document.getElementById('time');

    if (year) {
        year.textContent = new Date().getFullYear();
    }

    const applyTheme = (theme) => {
        if (theme === 'dark-mode') {
            document.body.classList.add('dark-mode');
            themeToggles.forEach(toggle => toggle.textContent = '☀️');
        } else {
            document.body.classList.remove('dark-mode');
            themeToggles.forEach(toggle => toggle.textContent = '🌙');
        }
    };

    // Apply the saved theme on page load
    if (currentTheme) {
        applyTheme(currentTheme);
    }

    themeToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const theme = document.body.classList.contains('dark-mode') ? 'dark-mode' : 'light-mode';
            localStorage.setItem('theme', theme);
            applyTheme(theme);
        });
    });
});