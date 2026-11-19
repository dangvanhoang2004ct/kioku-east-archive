export function readLocalJson(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : undefined;
  } catch {
    return undefined;
  }
}

export function writeLocalJson(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {}
}

export function removeLocalValue(key) {
  try {
    localStorage.removeItem(key);
  } catch {}
}

export function previewStorageHost() {
  try {
    return window.parent && window.parent !== window ? window.parent : window;
  } catch {
    return window;
  }
}
