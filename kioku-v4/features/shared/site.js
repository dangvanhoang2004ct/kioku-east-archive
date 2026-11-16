import {getFavorites} from '../storefront/favorites.js';
import {REFERENCES} from '../catalog/records.js';
const toggle=document.querySelector('[data-menu-toggle]'),menu=document.querySelector('[data-menu]');
function closeNav({restore=false}={}){if(!menu||!toggle)return;const wasOpen=menu.classList.contains('is-open');menu.classList.remove('is-open');toggle.setAttribute('aria-expanded','false');toggle.textContent='Menu';if(restore&&wasOpen)toggle.focus();}
if(toggle&&menu){
 toggle.addEventListener('click',()=>{const open=!menu.classList.contains('is-open');menu.classList.toggle('is-open',open);toggle.setAttribute('aria-expanded',String(open));toggle.textContent=open?'Close':'Menu';});
 menu.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeNav));
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&menu.classList.contains('is-open'))closeNav({restore:true})});
 document.addEventListener('pointerdown',e=>{if(!menu.contains(e.target)&&!toggle.contains(e.target))closeNav()});
}
function updateSavedCount(){document.querySelectorAll('[data-saved-count]').forEach(n=>n.textContent=String(getFavorites().length));}
window.addEventListener('kioku-favorites-changed',updateSavedCount);updateSavedCount();
const dialog=document.querySelector('[data-search-dialog]'),input=dialog?.querySelector('[data-global-search]'),result=dialog?.querySelector('[data-search-results]');let searchTrigger=null;
const escapeHTML=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function searchResults(){if(!input||!result)return;const q=input.value.trim().toLowerCase();const hits=REFERENCES.filter(x=>[x.maker,x.line,x.title,x.category].some(v=>v.toLowerCase().includes(q))).slice(0,6);
 result.innerHTML=hits.map(x=>`<a class="search-hit" href="./work.html?ref=${encodeURIComponent(x.slug)}"><span>${escapeHTML(x.maker)} / ${escapeHTML(x.category)}</span><strong>${escapeHTML(x.line)}</strong></a>`).join('')+(q?`<a class="search-all" href="./collection.html?q=${encodeURIComponent(q)}">View all catalogue results for “${escapeHTML(q)}”</a>`:'');
 if(!hits.length)result.innerHTML=`<p class="search-empty">No reference line matches this search. Try a maker or a series name.</p><a class="search-all" href="./collection.html">Open the full catalogue</a>`;
}
function openSearch(e){closeNav();if(!dialog)return;searchTrigger=e?.currentTarget||document.activeElement;if(typeof dialog.showModal==='function'&&!dialog.open)dialog.showModal();else dialog.setAttribute('open','');input.value='';searchResults();input.focus();}
function closeSearch(){if(!dialog)return;if(typeof dialog.close==='function'&&dialog.open)dialog.close();else dialog.removeAttribute('open');searchTrigger?.focus();}
document.querySelectorAll('[data-open-search]').forEach(btn=>btn.addEventListener('click',e=>openSearch(e)));
dialog?.querySelector('[data-close-search]')?.addEventListener('click',closeSearch);
dialog?.addEventListener('click',e=>{if(e.target===dialog)closeSearch()});
input?.addEventListener('input',searchResults);
document.addEventListener('keydown',e=>{const target=e.target;const editing=target instanceof HTMLElement&&(target.isContentEditable||['INPUT','TEXTAREA','SELECT'].includes(target.tagName));if((e.key==='/'&&!editing)||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k')){e.preventDefault();openSearch()}if(e.key==='Escape'&&dialog?.open)closeSearch()});
