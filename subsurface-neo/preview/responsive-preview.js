// Responsive interaction layer for the Subsurface Neo design preview.
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
  const graph = profile.querySelector('svg');
  const crosshair = profile.querySelector('.crosshair');
  const samplePoints = [...profile.querySelectorAll('[data-point]')];

  function yAtX(path, targetX) {
    let low = 0;
    let high = path.getTotalLength();
    for (let index = 0; index < 16; index += 1) {
      const middle = (low + high) / 2;
      if (path.getPointAtLength(middle).x < targetX) low = middle;
      else high = middle;
    }
    return path.getPointAtLength((low + high) / 2).y;
  }

  function inspectProfile(event) {
    const bounds = profile.getBoundingClientRect();
    const graphBounds = graph.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (event.clientX - graphBounds.left) / graphBounds.width));
    const graphX = ratio * 1000;

    profile.classList.add('inspecting');
    crosshair.setAttribute('x1', graphX);
    crosshair.setAttribute('x2', graphX);
    samplePoints.forEach(point => {
      const series = profile.querySelector(`[data-series="${point.dataset.point}"]`);
      point.setAttribute('cx', graphX);
      if (series) point.setAttribute('cy', yAtX(series, graphX));
    });

    const pointerX = event.clientX - bounds.left;
    const gap = 14;
    const tooltipWidth = tooltip.offsetWidth;
    let tooltipLeft = pointerX + gap;
    if (tooltipLeft + tooltipWidth > bounds.width - 4) tooltipLeft = pointerX - tooltipWidth - gap;
    tooltipLeft = Math.max(4, Math.min(bounds.width - tooltipWidth - 4, tooltipLeft));
    tooltip.style.left = `${tooltipLeft}px`;
    tooltip.querySelector('b').textContent = `${String(Math.round(ratio * 48)).padStart(2, '0')}:00`;
  }

  profile.addEventListener('pointermove', inspectProfile);
  profile.addEventListener('pointerdown', inspectProfile);
  profile.addEventListener('pointerleave', event => {
    if (event.pointerType !== 'touch') profile.classList.remove('inspecting');
  });
  document.addEventListener('pointerdown', event => {
    if (!profile.contains(event.target)) profile.classList.remove('inspecting');
  });
}

showView(location.hash.slice(1) || 'dashboard');
