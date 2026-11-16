document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        const isActive = href === currentPath || (href !== '/' && currentPath.startsWith(href));

        if (isActive) {
            link.classList.add('active');
        }
    });
});
