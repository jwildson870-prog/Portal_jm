(function () {
  'use strict';

  const root = document.documentElement;
  const THEME_KEY = 'portaljm-theme';
  const LAYOUT_KEY = 'portaljm-layout';
  const media = window.matchMedia('(prefers-color-scheme: dark)');

  function getTheme() {
    return localStorage.getItem(THEME_KEY) || 'system';
  }

  function isDark(theme) {
    return theme === 'dark' || (theme === 'system' && media.matches);
  }

  function applyTheme(theme) {
    const safeTheme = ['light', 'dark', 'system'].includes(theme) ? theme : 'system';
    root.dataset.themePreference = safeTheme;
    root.dataset.theme = isDark(safeTheme) ? 'dark' : 'light';

    const toggle = document.getElementById('themeToggle');
    if (toggle) {
      const dark = root.dataset.theme === 'dark';
      toggle.textContent = dark ? '☀️' : '🌙';
      toggle.setAttribute('aria-label', dark ? 'Ativar modo claro' : 'Ativar modo escuro');
      toggle.title = dark ? 'Ativar modo claro' : 'Ativar modo escuro';
    }

    document.querySelectorAll('[data-theme]').forEach((button) => {
      const selected = button.dataset.theme === safeTheme;
      button.classList.toggle('selected', selected);
      button.setAttribute('aria-pressed', selected ? 'true' : 'false');
    });
  }

  function applyLayout(layout) {
    const safeLayout = ['auto', 'desktop', 'mobile'].includes(layout) ? layout : 'auto';
    root.classList.toggle('layout-mobile', safeLayout === 'mobile');
    root.classList.toggle('layout-desktop', safeLayout === 'desktop');

    document.querySelectorAll('[data-layout]').forEach((button) => {
      const selected = button.dataset.layout === safeLayout;
      button.classList.toggle('selected', selected);
      button.setAttribute('aria-pressed', selected ? 'true' : 'false');
    });
  }

  function closeSidebar() {
    const menu = document.getElementById('sideMenu');
    const overlay = document.getElementById('menuOverlay');
    const toggle = document.getElementById('menuToggle');
    menu?.classList.remove('open');
    overlay?.classList.remove('open');
    toggle?.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('menu-open');
  }

  function openSidebar() {
    const menu = document.getElementById('sideMenu');
    const overlay = document.getElementById('menuOverlay');
    const toggle = document.getElementById('menuToggle');
    menu?.classList.add('open');
    overlay?.classList.add('open');
    toggle?.setAttribute('aria-expanded', 'true');
    document.body.classList.add('menu-open');
  }

  function initSidebar() {
    const toggle = document.getElementById('menuToggle');
    const close = document.getElementById('menuClose');
    const overlay = document.getElementById('menuOverlay');

    toggle?.addEventListener('click', () => {
      const menu = document.getElementById('sideMenu');
      if (menu?.classList.contains('open')) closeSidebar();
      else openSidebar();
    });
    close?.addEventListener('click', closeSidebar);
    overlay?.addEventListener('click', closeSidebar);

    document.querySelectorAll('#sideMenu a').forEach((link) => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 900) closeSidebar();
      });
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > 900) closeSidebar();
    });
  }

  function init() {
    applyTheme(getTheme());
    applyLayout(localStorage.getItem(LAYOUT_KEY) || 'auto');
    initSidebar();

    document.getElementById('themeToggle')?.addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem(THEME_KEY, next);
      applyTheme(next);
    });

    document.querySelectorAll('[data-theme]').forEach((button) => {
      button.addEventListener('click', () => {
        const theme = button.dataset.theme;
        localStorage.setItem(THEME_KEY, theme);
        applyTheme(theme);
      });
    });

    document.querySelectorAll('[data-layout]').forEach((button) => {
      button.addEventListener('click', () => {
        const layout = button.dataset.layout;
        localStorage.setItem(LAYOUT_KEY, layout);
        applyLayout(layout);
        if (window.innerWidth <= 900) closeSidebar();
      });
    });

    media.addEventListener?.('change', () => {
      if (getTheme() === 'system') applyTheme('system');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
