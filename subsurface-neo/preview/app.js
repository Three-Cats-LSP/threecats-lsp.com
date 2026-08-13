const views = [...document.querySelectorAll('.view')];
const navButtons = [...document.querySelectorAll('[data-view]')];

function showView(name) {
  const target = document.getElementById(name);
  if (!target) return;
  views.forEach(view => view.classList.toggle('active', view === target));
  document.querySelectorAll('.nav-item, .bottom-nav button').forEach(button => {
    const buttonView = button.dataset.view;
    button.classList.toggle('active', buttonView === name || (name === 'detail' && buttonView === 'dives'));
  });
  window.scrollTo({ top: 0, behavior: 'smooth' });
  history.replaceState(null, '', `#${name}`);
}

navButtons.forEach(button => button.addEventListener('click', () => showView(button.dataset.view)));
document.querySelectorAll('[data-open-dive]').forEach(card => card.addEventListener('click', () => showView('detail')));

document.querySelectorAll('.filters button').forEach(button => button.addEventListener('click', () => {
  button.parentElement.querySelectorAll('button').forEach(item => item.classList.remove('selected'));
  button.classList.add('selected');
}));

document.querySelectorAll('.graph-controls button[data-line]').forEach(button => button.addEventListener('click', () => {
  button.classList.toggle('on');
  const series = document.querySelector(`[data-series="${button.dataset.line}"]`);
  if (series) series.style.opacity = button.classList.contains('on') ? '1' : '.08';
}));

const profile = document.getElementById('large-profile');
const tooltip = document.getElementById('graph-tooltip');
if (profile && tooltip) {
  profile.addEventListener('pointermove', event => {
    const bounds = profile.getBoundingClientRect();
    const x = Math.max(.08, Math.min(.9, (event.clientX - bounds.left) / bounds.width));
    tooltip.style.left = `${Math.min(72, Math.max(18, x * 100))}%`;
    tooltip.querySelector('b').textContent = `${String(Math.round(x * 48)).padStart(2, '0')}:00`;
  });
}

showView(location.hash.slice(1) || 'dashboard');
