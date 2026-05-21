import { initMap, flyTo } from './map.js';
import { attachMarkersLayer, clearMarkers, addUserMarker, addPharmacyMarker } from './markers.js';
import { initFilters, filterUsers, filterPharmacies } from './filters.js';
import { initAlerts } from './alerts.js';
import { getUsers, getPharmacies } from './api.js';
import { signOut } from './auth.js';

let _allUsers = [];
let _allPharmacies = [];

function _stockBadge(stock) {
  if (stock == null) return '';
  const cls = stock <= 3 ? 'badge--danger' : stock <= 7 ? 'badge--warning' : 'badge--success';
  return `<span class="badge ${cls}" title="Stock restant">${stock}</span>`;
}

function renderSidebar(users, pharmacies) {
  const container = document.getElementById('sidebar-results');
  if (!container) return;
  container.innerHTML = '';

  pharmacies.forEach(p => {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.innerHTML = `
      <div class="result-card__name">${p.name}</div>
      <div class="result-card__meta">${p.address ?? ''} · ${p.phone ?? ''}</div>
      <div class="result-card__tags">
        ${p.is_garde ? '<span class="result-card__tag result-card__tag--garde">De garde</span>' : ''}
        ${p.garde_horaires ? `<span class="result-card__meta" style="font-size:0.75rem;">${p.garde_horaires.debut ?? ''}–${p.garde_horaires.fin ?? ''}</span>` : ''}
      </div>
    `;
    card.addEventListener('click', () => flyTo(p.latitude, p.longitude));
    container.appendChild(card);
  });

  users.forEach(u => {
    const card = document.createElement('div');
    card.className = 'result-card';
    const meds = (u.medicaments ?? []).map(m =>
      `<span class="result-card__tag">${m.nom}${m.dosage ? ' ' + m.dosage : ''} ${_stockBadge(m.stock_restant)}</span>`
    ).join('');
    card.innerHTML = `
      <div class="result-card__name">${u.pseudo}</div>
      <div class="result-card__meta">${(u.pathologies ?? []).join(', ') || 'Pathologie non renseignée'}</div>
      <div class="result-card__tags">${meds}</div>
    `;
    card.addEventListener('click', () => flyTo(u.latitude, u.longitude));
    container.appendChild(card);
  });

  if (!users.length && !pharmacies.length) {
    container.innerHTML = '<p style="color:var(--color-text-muted);font-size:0.85rem;padding:var(--spacing-sm);">Aucun résultat.</p>';
  }
}

function refresh({ filter, query }) {
  const users = filterUsers(_allUsers, { filter, query });
  const pharmacies = filterPharmacies(_allPharmacies, { filter, query });

  clearMarkers();
  users.forEach(addUserMarker);
  pharmacies.forEach(addPharmacyMarker);
  renderSidebar(users, pharmacies);
}

async function main() {
  initMap('map');
  attachMarkersLayer();
  initFilters(refresh);

  document.getElementById('btn-logout')?.addEventListener('click', (e) => {
    e.preventDefault();
    signOut();
  });

  try {
    [_allUsers, _allPharmacies] = await Promise.all([getUsers(), getPharmacies()]);
    refresh({ filter: 'all', query: '' });
  } catch (err) {
    console.error('Failed to load data:', err);
    const container = document.getElementById('sidebar-results');
    if (container) {
      container.innerHTML = `<p style="color:var(--color-danger);padding:var(--spacing-sm);">Erreur de chargement. Vérifiez que le serveur est démarré.</p>`;
    }
  }
}

main();
initAlerts();
