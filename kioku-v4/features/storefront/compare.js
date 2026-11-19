import { previewStorageHost, readLocalJson, removeLocalValue, writeLocalJson } from '../../data/browser-storage.js';

const COMPARE_KEY = 'kioku.reference.compare.v1';
const validCompareIds = new Set(['ichiban-kuji', 'banpresto', 'ichibansho', 'pop', 'lookup', 'gem']);

export function selectedCompare() {
  const saved = readLocalJson(COMPARE_KEY);
  const entries = saved === undefined ? previewStorageHost().__KIOKU_COMPARE : saved;
  return Array.isArray(entries) ? entries.filter(id => validCompareIds.has(id)).slice(0, 3) : [];
}

export function compareToggle(slug) {
  const next = selectedCompare();
  if (next.includes(slug)) next.splice(next.indexOf(slug), 1);
  else if (next.length < 3) next.push(slug);
  else return { ok: false, next };

  writeLocalJson(COMPARE_KEY, next);
  previewStorageHost().__KIOKU_COMPARE = next;
  return { ok: true, next };
}

export function compareClear() {
  removeLocalValue(COMPARE_KEY);
  previewStorageHost().__KIOKU_COMPARE = [];
}
