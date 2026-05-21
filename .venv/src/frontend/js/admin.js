import { getPharmacies } from './api.js';

const formPharmacy = document.getElementById('form-pharmacy');
const gardeTable = document.getElementById('garde-table');
const alertContainer = document.getElementById('alert-container');

function showAlert(message, type = 'danger') {
  if (alertContainer) alertContainer.innerHTML = `<div class="alert alert--${type}">${message}</div>`;
}

async function loadGardeList() {
  try {
    const pharmacies = await getPharmacies(true);
    if (!gardeTable) return;

    if (!pharmacies.length) {
      gardeTable.innerHTML = '<p style="color:var(--color-text-muted);">Aucune pharmacie de garde.</p>';
      return;
    }

    gardeTable.innerHTML = `
      <table style="width:100%;border-collapse:collapse;font-size:0.9rem;">
        <thead>
          <tr style="border-bottom:2px solid var(--color-border);">
            <th style="text-align:left;padding:6px 8px;">Nom</th>
            <th style="text-align:left;padding:6px 8px;">Date</th>
            <th style="text-align:left;padding:6px 8px;">Horaires</th>
          </tr>
        </thead>
        <tbody>
          ${pharmacies.map(p => `
            <tr style="border-bottom:1px solid var(--color-border);">
              <td style="padding:6px 8px;">${p.name}</td>
              <td style="padding:6px 8px;">${p.garde_horaires?.date ?? '—'}</td>
              <td style="padding:6px 8px;">${p.garde_horaires?.debut ?? ''} – ${p.garde_horaires?.fin ?? ''}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  } catch (err) {
    if (gardeTable) gardeTable.innerHTML = `<p style="color:var(--color-danger);">${err.message}</p>`;
  }
}

formPharmacy?.addEventListener('submit', async (e) => {
  e.preventDefault();
  showAlert('Fonctionnalité disponible en Phase 1 (connexion Supabase requise).', 'success');
});

document.getElementById('btn-logout')?.addEventListener('click', (e) => {
  e.preventDefault();
  import('./auth.js').then(m => m.signOut());
});

loadGardeList();
