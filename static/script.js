// Navbar mobile menu
const menuBtn = document.getElementById('menuBtn');
const navLinks = document.querySelector('.nav-links');

if (menuBtn) {
  menuBtn.addEventListener('click', () => {
    if (navLinks.classList.contains('open')) {
      navLinks.classList.remove('open');
    } else {
      navLinks.classList.add('open');
    }
  });
}

// Auto hide flash messages after 3 seconds
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(flash => {
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transition = 'opacity 0.5s';
      setTimeout(() => flash.remove(), 500);
    }, 3000);
  });
});