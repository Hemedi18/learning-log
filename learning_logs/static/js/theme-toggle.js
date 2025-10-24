document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme');
    const year = document.getElementById('time');

    year.textContent = new Date().getFullYear();

    // Apply the saved theme on page load
    if (currentTheme) {
        document.body.classList.add(currentTheme);
        if (themeToggle) {
            themeToggle.textContent = currentTheme === 'dark-mode' ? '☀️' : '🌙';
        }
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');

            let theme = document.body.classList.contains('dark-mode') ? 'dark-mode' : '';
            localStorage.setItem('theme', theme);
            
            themeToggle.textContent = theme === 'dark-mode' ? '☀️' : '🌙';
        });
    }
});