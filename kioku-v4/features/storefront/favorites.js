const KEY='kioku.editorial.saved.v3';
function sessionHost(){try{return window.parent&&window.parent!==window?window.parent:window}catch{return window}}
function fallback(){const h=sessionHost();return Array.isArray(h.__KIOKU_SAVED)?h.__KIOKU_SAVED:[]}
export function getFavorites(){try{const raw=localStorage.getItem(KEY);if(raw){const data=JSON.parse(raw);return Array.isArray(data)?data.filter(x=>typeof x==='string'):fallback()}}catch{}return fallback()}
export function isFavorite(id){return getFavorites().includes(id)}
export function toggleFavorite(id){const next=new Set(getFavorites());next.has(id)?next.delete(id):next.add(id);const values=[...next];try{localStorage.setItem(KEY,JSON.stringify(values))}catch{};sessionHost().__KIOKU_SAVED=values;window.dispatchEvent(new Event('kioku-favorites-changed'));return next.has(id)}
