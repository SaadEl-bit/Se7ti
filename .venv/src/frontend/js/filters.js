let _currentFilter = 'all';
let _searchQuery = '';
let _onChangeCallback = null;

export function initFilters(onChangeCallback) {
  _onChangeCallback = onChangeCallback;

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      _currentFilter = btn.dataset.filter;
      _onChangeCallback?.({ filter: _currentFilter, query: _searchQuery });
    });
  });

  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      _searchQuery = e.target.value.toLowerCase().trim();
      _onChangeCallback?.({ filter: _currentFilter, query: _searchQuery });
    });
  }
}

export function filterUsers(users, { filter, query }) {
  if (filter === 'pharmacies' || filter === 'garde') return [];
  return users.filter(u => {
    if (!query) return true;
    const inPseudo = u.pseudo?.toLowerCase().includes(query);
    const inMeds = (u.medicaments ?? []).some(m => m.nom?.toLowerCase().includes(query));
    return inPseudo || inMeds;
  });
}

export function filterPharmacies(pharmacies, { filter, query }) {
  if (filter === 'patients') return [];
  let result = pharmacies;
  if (filter === 'garde') result = result.filter(p => p.is_garde);
  if (query) result = result.filter(p => p.name?.toLowerCase().includes(query));
  return result;
}
