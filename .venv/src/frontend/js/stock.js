import { getMedicationStatus, logConsumption, searchMedications } from './api.js';
import { getCurrentUser } from './auth.js';
import { initAlerts } from './alerts.js';

const medGrid = document.getElementById('med-grid');
const formConsumption = document.getElementById('form-consumption');
const alertContainer = document.getElementById('alert-container');
const medSearch = document.getElementById('med-search');
const medSuggestions = document.getElementById('med-suggestions');
const consumeMedId = document.getElementById('consume-med-id');

let _userMedications = [];
let _activeSuggestionIndex = -1;

function showAlert(message, type = 'danger') {
  if (alertContainer) alertContainer.innerHTML = `<div class="alert alert--${type}">${message}</div>`;
}

// ── Med grid ──────────────────────────────────────────────────────────────────

function _stockClass(qty, threshold) {
  if (qty <= Math.floor(threshold / 2)) return 'low';
  if (qty <= threshold) return 'warning';
  return '';
}

function renderMedGrid(medications) {
  if (!medGrid) return;
  if (!medications.length) {
    medGrid.innerHTML = '<p style="color:var(--color-text-muted);">Aucun médicament suivi.</p>';
    return;
  }
  medGrid.innerHTML = medications.map(med => {
    const cls = _stockClass(med.stock_quantity, med.alert_threshold);
    return `
      <div class="card med-card ${cls}">
        <div class="med-name">${med.name} <small style="font-weight:400;color:var(--color-text-muted);">${med.dosage ?? ''}</small></div>
        <div class="med-qty ${cls}">${med.stock_quantity}</div>
        <div style="font-size:0.82rem;color:var(--color-text-muted);">${med.stock_unit}</div>
        ${cls === 'low'     ? '<span class="badge badge--danger"  style="margin-top:4px;">Stock critique</span>' : ''}
        ${cls === 'warning' ? '<span class="badge badge--warning" style="margin-top:4px;">Stock bas</span>'      : ''}
      </div>
    `;
  }).join('');
}

// ── Autocomplete ──────────────────────────────────────────────────────────────

function hideSuggestions() {
  if (medSuggestions) medSuggestions.style.display = 'none';
  _activeSuggestionIndex = -1;
}

function renderSuggestions(items) {
  if (!medSuggestions) return;
  if (!items.length) {
    medSuggestions.innerHTML = '<div class="autocomplete-item disabled">Aucun résultat</div>';
  } else {
    medSuggestions.innerHTML = items.map((item, i) => {
      const isUser = !!item.id;
      return `<div class="autocomplete-item" data-index="${i}" data-id="${item.id ?? ''}" data-name="${item.name}">
        ${item.name}${item.dosage ? ' <small>' + item.dosage + '</small>' : ''}
        ${isUser ? ' <small style="color:#28a745;">✓ suivi</small>' : ''}
      </div>`;
    }).join('');
  }
  medSuggestions.style.display = '';
  _activeSuggestionIndex = -1;
}

function selectSuggestion(name, id) {
  if (medSearch) medSearch.value = name;
  if (consumeMedId) consumeMedId.value = id;
  hideSuggestions();
}

if (medSuggestions) {
  medSuggestions.addEventListener('mousedown', (e) => {
    const item = e.target.closest('.autocomplete-item');
    if (!item || item.classList.contains('disabled')) return;
    selectSuggestion(item.dataset.name, item.dataset.id);
  });
}

if (medSearch) {
  medSearch.addEventListener('input', async () => {
    const q = medSearch.value.trim();
    if (consumeMedId) consumeMedId.value = '';

    const userMatches = _userMedications.filter(m =>
      !q || m.name.toLowerCase().includes(q.toLowerCase())
    );

    let knownMatches = [];
    if (q.length >= 2) {
      try {
        const res = await searchMedications(q);
        knownMatches = (res.results ?? []).filter(
          name => !userMatches.some(m => m.name.toLowerCase() === name.toLowerCase())
        );
      } catch (_) {}
    }

    const combined = [
      ...userMatches,
      ...knownMatches.map(name => ({ name, id: '', dosage: null })),
    ];

    if (!combined.length && !q) { hideSuggestions(); return; }
    renderSuggestions(combined);
  });

  medSearch.addEventListener('focus', () => {
    if (_userMedications.length) renderSuggestions(_userMedications);
  });

  medSearch.addEventListener('keydown', (e) => {
    const items = medSuggestions?.querySelectorAll('.autocomplete-item:not(.disabled)') ?? [];
    if (!items.length) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      _activeSuggestionIndex = Math.min(_activeSuggestionIndex + 1, items.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      _activeSuggestionIndex = Math.max(_activeSuggestionIndex - 1, 0);
    } else if (e.key === 'Enter' && _activeSuggestionIndex >= 0) {
      e.preventDefault();
      const active = items[_activeSuggestionIndex];
      selectSuggestion(active.dataset.name, active.dataset.id);
      return;
    } else if (e.key === 'Escape') {
      hideSuggestions(); return;
    }
    items.forEach((el, i) => el.classList.toggle('highlighted', i === _activeSuggestionIndex));
  });

  document.addEventListener('click', (e) => {
    if (!medSearch.contains(e.target) && !medSuggestions?.contains(e.target)) hideSuggestions();
  });
}

// ── Data loading ──────────────────────────────────────────────────────────────

async function loadMedications() {
  try {
    const user = await getCurrentUser();
    const userId = user?.id ?? 'b1000000-0000-0000-0000-000000000001';
    const data = await getMedicationStatus(userId);
    _userMedications = data.medications ?? [];
    renderMedGrid(_userMedications);
  } catch (err) {
    if (medGrid) medGrid.innerHTML = `<p style="color:var(--color-danger);">${err.message}</p>`;
  }
}

// ── Consumption form ──────────────────────────────────────────────────────────

formConsumption?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const medId   = consumeMedId?.value;
  const medName = medSearch?.value?.trim();

  if (!medName) { showAlert('Sélectionnez un médicament.'); return; }

  try {
    const user = await getCurrentUser();
    await logConsumption(
      user?.id ?? 'b1000000-0000-0000-0000-000000000001',
      medId || medName,
      parseInt(document.getElementById('consumption-qty').value, 10),
    );
    showAlert(`Prise de ${medName} enregistrée.`, 'success');
    if (medSearch) medSearch.value = '';
    if (consumeMedId) consumeMedId.value = '';
    loadMedications();
  } catch (err) {
    showAlert(err.message);
  }
});

document.getElementById('btn-logout')?.addEventListener('click', (e) => {
  e.preventDefault();
  import('./auth.js').then(m => m.signOut());
});

loadMedications();
initAlerts();
