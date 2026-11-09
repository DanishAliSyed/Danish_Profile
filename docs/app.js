import { github, raw, parseCatalog, selectProjects } from './catalog.js';

const byId = id => document.getElementById(id);
const search = byId('search');
const sort = byId('sort');
const filters = byId('filters');
const cards = byId('cards');
const count = byId('count');
const template = byId('project-card');
let projects = [];
const params = new URLSearchParams(location.search);
search.value = params.get('q') || '';
sort.value = ['featured','index','az'].includes(params.get('sort')) ? params.get('sort') : 'featured';
let topic = params.get('topic') || '';

function syncUrl() {
  const url = new URL(location.href);
  for (const [key, val] of Object.entries({q: search.value.trim(), topic, sort: sort.value === 'featured' ? '' : sort.value})) {
    if (val) url.searchParams.set(key, val); else url.searchParams.delete(key);
  }
  history.replaceState(null, '', url);
}
function makeCard(project) {
  const card = template.content.cloneNode(true);
  const link = card.querySelector('.case-link');
  link.textContent = project.title;
  link.href = github + project.slug + '/README.md';
  const label = card.querySelector('.category');
  label.textContent = project.topic;
  card.querySelector('.description').textContent = project.description;
  const tags = card.querySelector('.tags');
  for (const tool of project.tools) {
    const tag = document.createElement('li');
    tag.textContent = tool;
    tags.append(tag);
  }
  tags.hidden = !project.tools.length;
  if (project.artifact) {
    const link = document.createElement('a');
    link.href = github + project.slug + '/' + project.artifact[0];
    link.textContent = project.artifact[1];
    card.querySelector('.card-links').append(link);
  }
  return card;
}
function render() {
  const selected = selectProjects(projects, {query: search.value, topic, sort: sort.value});
  for (const button of filters.children) button.setAttribute('aria-pressed', String(button.dataset.topic === topic));
  cards.replaceChildren(...selected.map(makeCard));
  count.textContent = `Showing ${selected.length} of ${projects.length} projects`;
  if (!selected.length) {
    const panel = document.createElement('div');
    panel.className = 'empty';
    const message = document.createElement('p');
    message.textContent = 'No projects match this search. Try a different term or clear your filters.';
    const reset = document.createElement('button');
    reset.className = 'reset';
    reset.textContent = 'Clear search and filters';
    reset.addEventListener('click', () => {
      search.value = '';
      topic = '';
      render();
      search.focus();
    });
    panel.append(message, reset);
    cards.append(panel);
  }
  syncUrl();
}
function loadProjects(next) {
  const topics = [...new Set(next.map(p => p.topic))].sort();
  if (topic && !topics.includes(topic)) topic = '';
  const hadFilterFocus = filters.contains(document.activeElement);
  const focusedTopic = hadFilterFocus ? document.activeElement.dataset.topic : null;
  projects = next;
  filters.replaceChildren(...['', ...topics].map(value => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = value || 'All projects';
    button.dataset.topic = value;
    button.addEventListener('click', () => { topic = value; render(); });
    return button;
  }));
  byId('controls').hidden = false;
  byId('fallback').hidden = true;
  render();
  if (hadFilterFocus) [...filters.children].find(button => button.dataset.topic === focusedTopic)?.focus();
}
async function getCatalog(url) {
  const response = await fetch(url, { credentials: 'omit', signal: AbortSignal.timeout(4500) });
  if (!response.ok) throw new Error('Catalog unavailable');
  const next = parseCatalog(await response.text());
  if (!next.length) throw new Error('Catalog is empty');
  return next;
}
search.addEventListener('input', render);
sort.addEventListener('change', render);
const snapshot = getCatalog('./project-index.md');
const latest = getCatalog(raw + 'README.md');
const first = await Promise.any([snapshot, latest]).catch(() => null);
if (first) loadProjects(first);
const refreshed = await latest.catch(() => null);
if (refreshed && JSON.stringify(refreshed) !== JSON.stringify(first)) loadProjects(refreshed);
