export const OUJDA = [34.686, -1.911];
export const DEFAULT_ZOOM = 14;

let _map = null;

export function initMap(containerId = 'map') {
  _map = L.map(containerId).setView(OUJDA, DEFAULT_ZOOM);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 19,
  }).addTo(_map);

  return _map;
}

export function getMap() {
  return _map;
}

export function flyTo(lat, lon, zoom = 16) {
  _map?.flyTo([lat, lon], zoom, { animate: true, duration: 0.8 });
}
