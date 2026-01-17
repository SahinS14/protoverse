document.addEventListener('DOMContentLoaded', () => {
// Language loader for AstroGuard dashboard using data-lang attributes

async function loadLanguage(lang = 'en') {
    const res = await fetch(`assets/lang/${lang}.json`);
    const langData = await res.json();
    window.lang = langData;
    applyLanguage(langData);
    // After language is loaded and applied, initialize map and dashboard
    if (typeof window.initMap === 'function') {
        window.initMap();
    }
    if (typeof window.loadDashboardStats === 'function') {
        window.loadDashboardStats();
    }
    if (typeof window.loadSatellites === 'function') {
        window.loadSatellites();
    }
}

function applyLanguage(langData) {
    // Replace textContent for elements with data-lang attributes
    document.querySelectorAll('[data-lang]').forEach(el => {
        const key = el.getAttribute('data-lang');
        if (langData[key]) {
            el.textContent = langData[key];
        }
    });
    // Replace placeholders for inputs with data-lang-placeholder
    document.querySelectorAll('[data-lang-placeholder]').forEach(el => {
        const key = el.getAttribute('data-lang-placeholder');
        if (langData[key]) {
            el.placeholder = langData[key];
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadLanguage('en');
});
