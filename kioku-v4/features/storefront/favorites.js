import { previewStorageHost, readLocalJson, writeLocalJson } from '../../data/browser-storage.js';

const KEY = 'kioku.editorial.saved.v3';

export function getFavorites() {
  const saved = readLocalJson(KEY);
  if (Array.isArray(saved)) return saved.filter(id => typeof id === 'string');

  const fallback = previewStorageHost().__KIOKU_SAVED;
  return Array.isArray(fallback) ? fallback : [];
}

export function isFavorite(id) {
  return getFavorites().includes(id);
}

export function toggleFavorite(id) {
  const next = new Set(getFavorites());
  if (next.has(id)) next.delete(id);
  else next.add(id);

  const values = [...next];
  writeLocalJson(KEY, values);
  previewStorageHost().__KIOKU_SAVED = values;
  window.dispatchEvent(new Event('kioku-favorites-changed'));
  return next.has(id);
}
