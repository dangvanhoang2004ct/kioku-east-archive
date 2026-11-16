import {REFERENCES} from '../catalog/records.js';
const form=document.querySelector('[data-finder-form]'),out=document.querySelector('[data-finder-results]'),grid=document.querySelector('[data-finder-recommendations]');
if(form){
 const safe=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
 form.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;
  const v=Object.fromEntries(new FormData(form).entries());
  const byMaker=REFERENCES.filter(r=>v.maker==='any'||r.maker===v.maker);
  const priority={dynamic:['ichiban-kuji','ichibansho','pop','gem','banpresto','lookup'],portrait:['pop','gem','banpresto','ichibansho','ichiban-kuji','lookup'],compact:['lookup','banpresto','ichiban-kuji','gem','pop','ichibansho']}[v.style];
  const candidates=byMaker.sort((a,b)=>priority.indexOf(a.slug)-priority.indexOf(b.slug)).slice(0,3);
  const mk=v.maker==='any'?'both maker families':v.maker;
  out.querySelector('[data-finder-message]').textContent=`Based on your interest in ${mk} and the way you like to display a collectible, these maker-line references may be useful starting points. This is an editorial suggestion, not a product match or stock check.`;
  grid.innerHTML=candidates.map(r=>`<a class="finder-pick" href="./work.html?ref=${encodeURIComponent(r.slug)}"><span>${safe(r.maker)} · ${safe(r.category)}</span><strong>${safe(r.line)}</strong><small>Open line reference ↗</small></a>`).join('');
  out.querySelector('[data-finder-box-guide]').textContent=v.box==='important'?'Packaging matters to you: for any real item, check actual box photographs, opening history if documented, and packaging wear separately from the figure.':v.box==='flexible'?'Open to no-box figures? Confirm the exact figure photos, included base, accessories and missing parts before considering a purchase.':'Unsure about packaging? Use the Condition Guide to compare figure, box, parts and disclosed flaws separately.';
  out.hidden=false;out.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});out.focus({preventScroll:true});
 });
 form.addEventListener('reset',()=>{out.hidden=true;grid.innerHTML=''});
}
