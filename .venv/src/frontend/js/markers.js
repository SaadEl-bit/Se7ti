import { getMap } from './map.js';

const _userIcon = L.divIcon({
  className: '',
  html: '<div style="width:14px;height:14px;border-radius:50%;background:#1a6eb5;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.4);"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

const _pharmacyIcon = L.divIcon({
  className: '',
  html: '<div style="width:16px;height:16px;border-radius:3px;background:#28a745;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.4);"></div>',
  iconSize: [16, 16],
  iconAnchor: [8, 8],
});

const _gardeIcon = L.divIcon({
  className: '',
  html: '<div style="width:18px;height:18px;border-radius:3px;background:#dc3545;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.4);"></div>',
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

const _layerGroup = L.layerGroup();

export function attachMarkersLayer() {
  const map = getMap();
  if (map) _layerGroup.addTo(map);
}

export function clearMarkers() {
  _layerGroup.clearLayers();
}

export function addUserMarker(user) {
  const meds = (user.medicaments ?? []).map(m => `${m.nom} ${m.dosage ?? ''}`).join(', ');
  const popup = `
    <div class="popup-title">${user.pseudo}</div>
    <div class="popup-meta">${(user.pathologies ?? []).join(', ') || 'Pathologie non renseignée'}</div>
    <div class="popup-meds">${meds || 'Aucun médicament'}</div>
  `;
  L.marker([user.latitude, user.longitude], { icon: _userIcon })
    .bindPopup(popup)
    .addTo(_layerGroup);
}

export function addPharmacyMarker(pharmacy) {
  const icon = pharmacy.is_garde ? _gardeIcon : _pharmacyIcon;
  const gardeBadge = pharmacy.is_garde
    ? '<span class="popup-garde-badge">De garde</span>'
    : '';
  const popup = `
    <div class="popup-title">${pharmacy.name}</div>
    <div class="popup-meta">${pharmacy.address ?? ''}</div>
    <div class="popup-meta">${pharmacy.phone ?? ''}</div>
    ${gardeBadge}
  `;
  L.marker([pharmacy.latitude, pharmacy.longitude], { icon })
    .bindPopup(popup)
    .addTo(_layerGroup);
}
