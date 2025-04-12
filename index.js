document.addEventListener('DOMContentLoaded', () => {
  const menuToggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('nav');
  
  menuToggle.addEventListener('click', () => {
    nav.classList.toggle('nav-active');
    menuToggle.classList.toggle('active');
    document.body.classList.toggle('menu-open');
  });

  // Close menu when clicking on a link (for mobile)
  const navLinks = document.querySelectorAll('nav a');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (nav.classList.contains('nav-active')) {
        nav.classList.remove('nav-active');
        menuToggle.classList.remove('active');
        document.body.classList.remove('menu-open');
      }
    });
  });
}); 