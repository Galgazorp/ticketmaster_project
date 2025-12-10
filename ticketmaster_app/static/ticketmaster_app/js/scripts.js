const darkModeToggle = document.getElementById('darkModeToggle');
const html = document.documentElement;

if (localStorage.getItem('theme') === 'dark') {
  html.setAttribute('data-bs-theme', 'dark');
  darkModeToggle.innerHTML = '<i class="bi bi-sun-fill"></i> Light Mode';
}

darkModeToggle.addEventListener('click', function() {
  const currentTheme = html.getAttribute('data-bs-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

  html.setAttribute('data-bs-theme', newTheme);
  localStorage.setItem('theme', newTheme);

  darkModeToggle.innerHTML = newTheme === 'dark'
    ? '<i class="bi bi-sun-fill"></i> Light Mode'
    : '<i class="bi bi-moon-fill"></i> Dark Mode';
});