import { getMatching } from './api.js';
import { clearMarkers, addUserMarker } from './markers.js';

export async function runMatching(medication, lat, lon, radiusKm = 5) {
  const result = await getMatching(medication, lat, lon, radiusKm);
  clearMarkers();
  (result.matching_users ?? []).forEach(addUserMarker);
  return result;
}
