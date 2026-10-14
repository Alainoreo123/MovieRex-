const API = '';
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const selectedGenres = [];
const selectedCast = [];
let toastTimer;

function showToast(message, isError = false) {
  const toast = $('#toast');
  toast.textContent = message;
  toast.classList.toggle('error', isError);
  toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.hidden = true; }, 4200);
}

function setLoading(button, loading, text) {
  if (loading) {
    button.dataset.originalText = button.querySelector('span').textContent;
    button.disabled = true;
    button.querySelector('span').textContent = text || 'Finding films…';
    button.querySelector('b').textContent = '…';
  } else {
    button.disabled = false;
    button.querySelector('span').textContent = button.dataset.originalText || 'Find films';
    button.querySelector('b').textContent = '↗';
  }
}

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  let data;
  try { data = await response.json(); } catch { data = {}; }
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}

function setupTabs() {
  $$('.mode-tab').forEach((tab) => tab.addEventListener('click', () => {
    const mode = tab.dataset.mode;
    $$('.mode-tab').forEach((item) => {
      const active = item === tab;
      item.classList.toggle('active', active);
      item.setAttribute('aria-selected', String(active));
    });
    $$('.mode-panel').forEach((panel) => {
      const active = panel.id === `panel-${mode}`;
      panel.classList.toggle('active', active);
      panel.hidden = !active;
    });
  }));
}

function hideSuggestions(box) {
  box.classList.remove('open');
  box.replaceChildren();
}

function renderSuggestions(box, items, onChoose) {
  box.replaceChildren();
  if (!items || !items.length) { box.classList.remove('open'); return; }
  items.forEach((item) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'suggestion-item';
    button.role = 'option';
    button.textContent = item;
    button.addEventListener('click', () => { onChoose(item); hideSuggestions(box); });
    box.appendChild(button);
  });
  box.classList.add('open');
}

function debounce(fn, delay = 180) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}

function setupSingleAutocomplete(input, box, endpoint, onChoose, minChars = 1) {
  const search = debounce(async () => {
    const query = input.value.trim();
    if (query.length < minChars) { hideSuggestions(box); return; }
    try {
      const data = await apiFetch(`${endpoint}?q=${encodeURIComponent(query)}`);
      renderSuggestions(box, data.suggestions, onChoose);
    } catch (error) { hideSuggestions(box); }
  });
  input.addEventListener('input', search);
  input.addEventListener('focus', search);
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') hideSuggestions(box);
    if (event.key === 'Enter' && box.classList.contains('open')) {
      const first = box.querySelector('button');
      if (first) { event.preventDefault(); first.click(); }
    }
  });
  document.addEventListener('click', (event) => {
    if (!input.contains(event.target) && !box.contains(event.target)) hideSuggestions(box);
  });
}

function renderChips(container, values, onRemove) {
  container.replaceChildren();
  values.forEach((value) => {
    const chip = document.createElement('span');
    chip.className = 'chip';
    const text = document.createElement('span');
    text.textContent = value;
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.setAttribute('aria-label', `Remove ${value}`);
    remove.textContent = '×';
    remove.addEventListener('click', () => onRemove(value));
    chip.append(text, remove);
    container.appendChild(chip);
  });
}

function setupMultiAutocomplete({ input, box, endpoint, selected, chips }) {
  const search = debounce(async () => {
    const query = input.value.trim();
    if (query.length < 1) { hideSuggestions(box); return; }
    try {
      const data = await apiFetch(`${endpoint}?q=${encodeURIComponent(query)}`);
      const suggestions = (data.suggestions || []).filter((item) => !selected.includes(item));
      renderSuggestions(box, suggestions, (item) => {
        selected.push(item);
        renderChips(chips, selected, (value) => {
          selected.splice(selected.indexOf(value), 1);
          renderChips(chips, selected, removeSelected);
        });
        input.value = '';
        input.focus();
      });
    } catch { hideSuggestions(box); }
  });
  function removeSelected(value) {
    const index = selected.indexOf(value);
    if (index >= 0) selected.splice(index, 1);
    renderChips(chips, selected, removeSelected);
  }
  input.addEventListener('input', search);
  input.addEventListener('focus', search);
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') hideSuggestions(box);
    if (event.key === 'Enter' && box.classList.contains('open')) {
      const first = box.querySelector('button');
      if (first) { event.preventDefault(); first.click(); }
    }
  });
  document.addEventListener('click', (event) => {
    if (!input.contains(event.target) && !box.contains(event.target)) hideSuggestions(box);
  });
}

function numberOrNull(id) {
  const raw = $(id).value.trim();
  return raw === '' ? null : Number(raw);
}

function showResults(results, modeTitle) {
  const section = $('#results-section');
  const grid = $('#results-grid');
  grid.replaceChildren();
  $('#results-title').textContent = modeTitle;
  $('#results-subtitle').textContent = results.length ? 'Ranked by how closely each film matches your preferences.' : 'Try changing your description or relaxing a filter.';
  $('#result-count').textContent = `${results.length} FILM${results.length === 1 ? '' : 'S'}`;
  section.hidden = false;
  if (!results.length) {
    const empty = document.createElement('div'); empty.className = 'empty-state';
    empty.textContent = 'No films matched those preferences. Try a broader description or wider filters.';
    grid.appendChild(empty);
  }
  results.forEach((movie, index) => {
    const card = document.createElement('article'); card.className = 'movie-card';
    const rank = document.createElement('div'); rank.className = 'movie-rank'; rank.textContent = String(index + 1).padStart(2, '0');
    const content = document.createElement('div'); content.className = 'movie-content';
    const title = document.createElement('h3'); title.className = 'movie-title'; title.textContent = movie.title || 'Untitled';
    const meta = document.createElement('div'); meta.className = 'movie-meta';
    if (movie.rating !== null && movie.rating !== undefined && movie.rating !== '') addPill(meta, `IMDb ${Number(movie.rating).toFixed(1)}`);
    if (movie.runtime !== null && movie.runtime !== undefined && movie.runtime !== '') addPill(meta, `${Math.round(Number(movie.runtime))} min`);
    if (movie.genre) String(movie.genre).split(/[, ]+/).filter(Boolean).slice(0, 3).forEach((genre) => addPill(meta, genre));
    const details = document.createElement('p'); details.className = 'movie-details';
    const director = movie.director && movie.director !== 'N/A' ? `Director · ${movie.director}` : '';
    const cast = movie.cast && movie.cast !== 'N/A' ? `Cast · ${movie.cast}` : '';
    details.textContent = [director, cast].filter(Boolean).join('  /  ');
    content.append(title, meta, details);
    card.append(rank, content);
    if (movie.similarity !== null && movie.similarity !== undefined) {
      const score = document.createElement('span'); score.className = 'movie-score';
      score.textContent = `${(Number(movie.similarity) * 100).toFixed(1)}% match`; card.appendChild(score);
    }
    grid.appendChild(card);
  });
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function addPill(parent, text) {
  const pill = document.createElement('span'); pill.className = 'meta-pill'; pill.textContent = text; parent.appendChild(pill);
}

function showLoading() {
  const section = $('#results-section'); const grid = $('#results-grid');
  section.hidden = false; grid.replaceChildren();
  const loading = document.createElement('div'); loading.className = 'loading-state';
  loading.innerHTML = '<span class="spinner"></span>Finding films that fit…'; grid.appendChild(loading);
  $('#results-title').textContent = 'Searching the collection…'; $('#results-subtitle').textContent = '';
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function setupForms() {
  $('#similar-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = event.submitter;
    const title = $('#movie-title').value.trim();
    if (!title) return;
    setLoading(button, true, 'Finding films…'); showLoading();
    try {
      const data = await apiFetch('/api/recommend/movie', { method: 'POST', body: JSON.stringify({ movie_title: title, n: Number($('#similar-count').value) }) });
      showResults(data.results || [], `Because you liked ${title}.`);
    } catch (error) { showToast(error.message, true); $('#results-section').hidden = true; }
    finally { setLoading(button, false); }
  });

  $('#custom-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = event.submitter;
    const payload = {
      description: $('#description').value.trim(), genres: [...selectedGenres], cast: [...selectedCast],
      director: $('#director-input').value.trim() || null,
      min_runtime: numberOrNull('#min-runtime'), max_runtime: numberOrNull('#max-runtime'),
      min_rating: numberOrNull('#min-rating'), max_rating: numberOrNull('#max-rating'),
      n: Number($('#custom-count').value)
    };
    if (!payload.description) { showToast('Please describe the kind of movie you want.', true); return; }
    if (payload.min_runtime !== null && payload.max_runtime !== null && payload.min_runtime > payload.max_runtime) { showToast('Minimum runtime cannot exceed maximum runtime.', true); return; }
    if (payload.min_rating !== null && payload.max_rating !== null && payload.min_rating > payload.max_rating) { showToast('Minimum rating cannot exceed maximum rating.', true); return; }
    setLoading(button, true, 'Finding films…'); showLoading();
    try {
      const data = await apiFetch('/api/recommend/custom', { method: 'POST', body: JSON.stringify(payload) });
      showResults(data.results || [], 'Films picked for your mood.');
    } catch (error) { showToast(error.message, true); $('#results-section').hidden = true; }
    finally { setLoading(button, false); }
  });
}

async function checkBackend() {
  try { await apiFetch('/api/health'); }
  catch { showToast('The Movie-Rex backend could not be reached. Start it with: python -m uvicorn app:app --reload', true); }
}

setupTabs();
setupForms();
setupSingleAutocomplete($('#movie-title'), $('#title-suggestions'), '/api/suggestions/titles', (value) => { $('#movie-title').value = value; });
setupMultiAutocomplete({ input: $('#genre-input'), box: $('#genre-suggestions'), endpoint: '/api/suggestions/genres', selected: selectedGenres, chips: $('#genre-chips') });
setupMultiAutocomplete({ input: $('#cast-input'), box: $('#cast-suggestions'), endpoint: '/api/suggestions/cast', selected: selectedCast, chips: $('#cast-chips') });
setupSingleAutocomplete($('#director-input'), $('#director-suggestions'), '/api/suggestions/directors', (value) => { $('#director-input').value = value; });
checkBackend();
