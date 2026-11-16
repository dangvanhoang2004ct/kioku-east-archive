import {findReference,REFERENCES} from '../catalog/records.js';
import {isFavorite,toggleFavorite} from './favorites.js';
const params=new URLSearchParams(location.search),id=params.get('ref'),ref=findReference(id);const root=document.querySelector('[data-detail]');
const safe=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const sources={
 'ichiban-kuji':['Bandai Spirits · Ichiban Kuji','https://www.bandaispirits.co.jp/e/about/'],
 banpresto:['Bandai Namco · Banpresto','https://shop.bandainamco-am.com/brands/'],
 ichibansho:['Bandai · Ichibansho','https://www.bandai.com/News/post/blog/product-spotlight-ichibansho-figures'],
 pop:['MegaHouse · Portrait.Of.Pirates','https://en.megahobby.jp/collections/portrait-of-pirates'],
 lookup:['MegaHouse · Lookup','https://en.megahobby.jp/collections/look-up-series'],
 gem:['MegaHouse · G.E.M. Series','https://en.megahobby.jp/collections/g-e-m-series']
};
if(!ref){
 root.innerHTML='<section class="detail-missing"><span class="section-eyebrow tiny">REFERENCE LIBRARY</span><h1>Reference not found</h1><p>This maker-line reference is not in the current catalogue.</p><a class="btn" href="./collection.html">Return to Collection</a></section>';
 document.title='Reference not found | KIOKU';
}else{
 document.title=`${ref.line} | KIOKU Reference Library`;
 const source=sources[ref.slug];
 root.innerHTML=`<figure class="detail-art"><img src="./assets/img/reference-plate.svg" alt="Abstract KIOKU editorial reference diagram for ${safe(ref.line)}. Not product photography." width="900" height="680"><button type="button" data-zoom aria-haspopup="dialog">Expand diagram</button><figcaption class="detail-caption">KIOKU editorial diagram · not product photography</figcaption></figure><section class="detail-copy"><div class="section-eyebrow tiny">${safe(ref.maker)} · Reference library</div><h1>${safe(ref.line)}</h1><p>${safe(ref.category)}. This entry identifies a maker line for further research; it does not represent a specific physical item.</p><div class="detail-actions"><button type="button" class="btn" data-save aria-pressed="${isFavorite(ref.slug)}">${isFavorite(ref.slug)?'Remove from saved':'Save reference'}</button><button type="button" data-copy>Copy reference link</button><span data-detail-feedback role="status" aria-live="polite"></span></div><dl class="detail-meta"><dt>Maker</dt><dd>${safe(ref.maker)}</dd><dt>Figure line</dt><dd>${safe(ref.line)}</dd><dt>Reference category</dt><dd>${safe(ref.category)}</dd><dt>Item status</dt><dd>No physical item documented</dd><dt>Figure condition</dt><dd>Not assessed</dd><dt>Box and parts</dt><dd>Not documented</dd><dt>Price and stock</dt><dd>Not listed</dd><dt>Official maker source</dt><dd><a class="source-link" href="${source[1]}" target="_blank" rel="noopener noreferrer">${source[0]} ↗</a></dd></dl><aside class="detail-note">Reference entry only · KIOKU is independent and does not claim maker authorization. No item, condition, authenticity, price, or stock is represented.</aside><p class="detail-guide"><a href="./condition-guide.html" class="text-link">Read the Condition Guide</a></p></section>`;
 const save=root.querySelector('[data-save]');save.addEventListener('click',()=>{const on=toggleFavorite(ref.slug);save.textContent=on?'Remove from saved':'Save reference';save.setAttribute('aria-pressed',String(on));});
 const copy=root.querySelector('[data-copy]'),feedback=root.querySelector('[data-detail-feedback]');copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);feedback.textContent='Reference link copied.';}catch{feedback.textContent='Copy the address from your browser bar.';}});
 const light=document.querySelector('[data-lightbox]');let previous=null;function open(){previous=document.activeElement;light.querySelector('img').alt=`Abstract KIOKU editorial reference diagram for ${ref.line}. Not product photography.`;light.classList.add('is-open');light.removeAttribute('aria-hidden');document.body.style.overflow='hidden';light.querySelector('[data-zoom-close]').focus();}function close(){light.classList.remove('is-open');light.setAttribute('aria-hidden','true');document.body.style.overflow='';(previous||root.querySelector('[data-zoom]')).focus();}
 root.querySelector('[data-zoom]').addEventListener('click',open);light.querySelector('[data-zoom-close]').addEventListener('click',close);light.addEventListener('click',e=>{if(e.target===light)close()});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&light.classList.contains('is-open'))close();if(e.key==='Tab'&&light.classList.contains('is-open')){e.preventDefault();light.querySelector('[data-zoom-close]').focus();}});
 const related=REFERENCES.filter(x=>x.maker===ref.maker&&x.slug!==ref.slug).slice(0,2);if(related.length){const section=document.querySelector('[data-related-lines]');section.innerHTML=`<h2>More ${safe(ref.maker)} lines</h2><div>${related.map(x=>`<a href="./work.html?ref=${encodeURIComponent(x.slug)}"><span>${safe(x.category)}</span><strong>${safe(x.line)}</strong><small>Open reference ↗</small></a>`).join('')}</div>`;}
}
