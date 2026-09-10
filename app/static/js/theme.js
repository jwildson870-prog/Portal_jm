(function(){
  const root=document.documentElement;
  function applyTheme(theme){
    const dark=theme==='dark'||(theme==='system'&&window.matchMedia('(prefers-color-scheme: dark)').matches);
    root.dataset.theme=dark?'dark':'light';
    const b=document.getElementById('themeToggle');
    if(b){b.textContent=dark?'☀️':'🌙';b.title=dark?'Ativar modo claro':'Ativar modo escuro';}
  }
  function applyLayout(layout){root.classList.remove('layout-mobile','layout-desktop');if(layout==='mobile')root.classList.add('layout-mobile');if(layout==='desktop')root.classList.add('layout-desktop');}
  const theme=localStorage.getItem('portaljm-theme')||'system';
  const layout=localStorage.getItem('portaljm-layout')||'auto';
  applyTheme(theme);applyLayout(layout);
  document.getElementById('themeToggle')?.addEventListener('click',()=>{const next=root.dataset.theme==='dark'?'light':'dark';localStorage.setItem('portaljm-theme',next);applyTheme(next);});
  document.querySelectorAll('[data-set-theme]').forEach(b=>b.addEventListener('click',()=>{localStorage.setItem('portaljm-theme',b.dataset.setTheme);applyTheme(b.dataset.setTheme);}));
  const menu=document.getElementById('sideMenu'),overlay=document.getElementById('sidebarOverlay');
  const close=()=>{menu?.classList.remove('open');overlay?.classList.remove('open')};
  document.getElementById('menuToggle')?.addEventListener('click',()=>{menu?.classList.add('open');overlay?.classList.add('open')});
  document.getElementById('sidebarClose')?.addEventListener('click',close);overlay?.addEventListener('click',close);
  menu?.querySelectorAll('a').forEach(a=>a.addEventListener('click',close));
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change',()=>{if((localStorage.getItem('portaljm-theme')||'system')==='system')applyTheme('system');});
})();
