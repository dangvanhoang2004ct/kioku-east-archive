const COMPARE_KEY='kioku.reference.compare.v1';
const validCompareIds=new Set(['ichiban-kuji','banpresto','ichibansho','pop','lookup','gem']);
function compareHost(){try{return window.parent&&window.parent!==window?window.parent:window}catch{return window}}
export function selectedCompare(){try{const raw=localStorage.getItem(COMPARE_KEY);if(raw){const data=JSON.parse(raw);return Array.isArray(data)?data.filter(x=>validCompareIds.has(x)).slice(0,3):[]}}catch{};const stored=compareHost().__KIOKU_COMPARE;return Array.isArray(stored)?stored.filter(x=>validCompareIds.has(x)).slice(0,3):[]}
export function compareToggle(slug){const next=selectedCompare();if(next.includes(slug)){next.splice(next.indexOf(slug),1)}else if(next.length<3)next.push(slug);else return {ok:false,next};try{localStorage.setItem(COMPARE_KEY,JSON.stringify(next))}catch{}compareHost().__KIOKU_COMPARE=next;return {ok:true,next}}
export function compareClear(){try{localStorage.removeItem(COMPARE_KEY)}catch{}compareHost().__KIOKU_COMPARE=[]}
