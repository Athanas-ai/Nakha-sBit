// Mobile menu toggle
function toggleMenu() {
    const nav = document.querySelector('nav');
    nav.classList.toggle('open');
    const toggle = document.querySelector('.nav-toggle');
    toggle.classList.toggle('active');
}

// Close menu when a link is clicked
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', () => {
        const nav = document.querySelector('nav');
        const toggle = document.querySelector('.nav-toggle');
        if (window.innerWidth < 640) {
            nav.classList.remove('open');
            toggle.classList.remove('active');
        }
    });
});
