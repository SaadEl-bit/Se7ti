const API_BASE = window.__ENV__?.API_BASE ?? 'http://localhost:8000/api';

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail ?? 'API error');
  }
  return response.json();
}

export async function getUsers() {
  return apiFetch('/users');
}

export async function getPharmacies(gardeOnly = false) {
  return apiFetch(`/pharmacies${gardeOnly ? '?garde_only=true' : ''}`);
}

export async function getPharmaciesOnDutyNow() {
  return apiFetch('/pharmacies/garde/now');
}

export async function getMatching(medication, lat, lon, radiusKm = 5) {
  const params = new URLSearchParams({ medication, lat, lon, radius_km: radiusKm });
  return apiFetch(`/matching?${params}`);
}

export async function uploadPrescription(userId, file) {
  const form = new FormData();
  form.append('user_id', userId);
  form.append('file', file);
  const response = await fetch(`${API_BASE}/prescriptions/upload`, { method: 'POST', body: form });
  if (!response.ok) throw new Error('Upload failed');
  return response.json();
}

export async function submitManualPrescription(userId, medications) {
  return apiFetch('/prescriptions/manual', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, medications }),
  });
}

export async function logConsumption(userId, medicationId, quantity, notes = '') {
  return apiFetch('/stock/consume', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, medication_id: medicationId, quantity, notes }),
  });
}

export async function getMedicationStatus(userId) {
  return apiFetch(`/stock/${userId}`);
}

export async function searchMedications(query) {
  return apiFetch(`/medications/search?q=${encodeURIComponent(query)}`);
}

export async function getAlerts(userId) {
  return apiFetch(`/alerts/${userId}`);
}
