document.addEventListener('DOMContentLoaded', () => {
  const loader = document.getElementById('pjm-loader');
  if (loader) {
    window.addEventListener('load', () => {
      setTimeout(() => loader.classList.add('hidden'), 180);
    }, { once: true });
    setTimeout(() => loader.classList.add('hidden'), 900);
  }
});
