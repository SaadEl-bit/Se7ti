import { getAlerts } from './api.js';
import { getCurrentUser } from './auth.js';

let _pollInterval = null;
// Track which alert keys were already toasted this session to avoid repeat toasts
const _SESSION_KEY = 'notified_alerts';
let _notified = new Set(JSON.parse(sessionStorage.getItem(_SESSION_KEY) || '[]'));

// ── Badge ─────────────────────────────────────────────────────────────────────

function _injectBadge() {
  const medLink = document.querySelector('a[href*="stock.html"]');
  if (!medLink || document.getElementById('notif-badge')) return;
  const badge = document.createElement('span');
  badge.id = 'notif-badge';
  badge.className = 'notif-badge';
  badge.style.display = 'none';
  medLink.appendChild(badge);
}

function _updateBadge(count) {
  const badge = document.getElementById('notif-badge');
  if (!badge) return;
  if (count > 0) {
    badge.textContent = count;
    badge.style.display = 'inline-flex';
  } else {
    badge.style.display = 'none';
  }
}

// ── Toasts ────────────────────────────────────────────────────────────────────

function _getToastContainer() {
  let c = document.getElementById('toast-container');
  if (!c) {
    c = document.createElement('div');
    c.id = 'toast-container';
    document.body.appendChild(c);
  }
  return c;
}

function _showToast(alert) {
  const container = _getToastContainer();
  const toast = document.createElement('div');
  toast.className = 'alert-toast';
  toast.innerHTML = `
    <strong>Stock bas — ${alert.medication_name ?? 'Médicament'}</strong>
    <span>${alert.message ?? 'Quantité insuffisante'}</span>
    <button class="toast-close" aria-label="Fermer">✕</button>
  `;
  toast.querySelector('.toast-close').addEventListener('click', () => toast.remove());
  container.appendChild(toast);
  setTimeout(() => { if (toast.parentElement) toast.remove(); }, 8000);
}

// ── Poll ──────────────────────────────────────────────────────────────────────

async function _poll(userId) {
  try {
    const { alerts } = await getAlerts(userId);
    _updateBadge(alerts.length);

    for (const alert of alerts) {
      const key = alert.medication_id ?? alert.medication_name;
      if (key && !_notified.has(key)) {
        _showToast(alert);
        _notified.add(key);
      }
    }
    sessionStorage.setItem(_SESSION_KEY, JSON.stringify([..._notified]));

    // Update alerts-section on the stock page if present (avoids double fetch in stock.js)
    const section = document.getElementById('alerts-section');
    if (section) {
      if (!alerts.length) { section.style.display = 'none'; return; }
      section.style.display = '';
      section.innerHTML = alerts.map(a => `<div class="alert-strip">⚠ ${a.message}</div>`).join('');
    }
  } catch {
    // Alerts are non-critical — silently ignore failures
  }
}

// ── Public API ────────────────────────────────────────────────────────────────

export async function initAlerts() {
  _injectBadge();
  try {
    const user = await getCurrentUser();
    const userId = user?.id ?? 'b1000000-0000-0000-0000-000000000001';
    await _poll(userId);
    if (_pollInterval) clearInterval(_pollInterval);
    _pollInterval = setInterval(() => _poll(userId), 60_000);
  } catch {
    // Auth may not be available on every page — skip silently
  }
}
