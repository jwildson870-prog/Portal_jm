(() => {
  const sidebar = document.getElementById('portalSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const toggle = document.getElementById('menuToggle');
  const close = document.getElementById('sidebarClose');
  const bottom = document.getElementById('bottomMenu');
  const search = document.getElementById('menuSearch');

  const isMobile = () => window.matchMedia('(max-width: 899px)').matches;
  const setMenu = (open) => {
    if (!sidebar) return;
    sidebar.classList.toggle('open', open);
    overlay?.classList.toggle('show', open);
    document.body.classList.toggle('menu-open', open);
    toggle?.setAttribute('aria-expanded', String(open));
  };

  // Menus start closed on mobile and are visible on desktop through CSS.
  setMenu(false);
  toggle?.addEventListener('click', () => setMenu(!sidebar?.classList.contains('open')));
  bottom?.addEventListener('click', () => setMenu(true));
  close?.addEventListener('click', () => setMenu(false));
  overlay?.addEventListener('click', () => setMenu(false));
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') setMenu(false); });
  window.addEventListener('resize', () => { if (!isMobile()) setMenu(false); });

  document.querySelectorAll('.side-link').forEach((link) => {
    link.addEventListener('click', () => { if (isMobile()) setMenu(false); });
  });

  search?.addEventListener('input', () => {
    const query = search.value.toLocaleLowerCase('pt-BR').trim();
    document.querySelectorAll('#sidebarNav .side-link').forEach((link) => {
      link.hidden = query && !link.innerText.toLocaleLowerCase('pt-BR').includes(query);
    });
  });

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => navigator.serviceWorker.register('/service-worker.js').catch(() => {}));
  }
})();
