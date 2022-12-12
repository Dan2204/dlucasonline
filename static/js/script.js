const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelectorAll('.nav__link');

navToggle.addEventListener('click', () => {
  document.body.classList.toggle('nav-open');
});

navLinks.forEach((link) => {
  link.addEventListener('click', () => {
    document.body.classList.remove('nav-open');
  });
});

const mq = window.matchMedia('(min-width: 800px)');
mq.addEventListener('change', () => {
  if (mq.matches) {
    document.body.classList.remove('nav-open');
  }
});

function checkToggle(q) {
  q.matches
    ? document.body.classList.remove('nav-available')
    : document.body.classList.add('nav-available');
}
const mq2 = window.matchMedia('(min-width: 800px)');
checkToggle(mq2);
mq2.addEventListener('change', checkToggle);
