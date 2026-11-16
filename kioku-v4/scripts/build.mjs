import {cpSync,rmSync,mkdirSync} from 'node:fs';
import {join,resolve} from 'node:path';
const base=resolve(import.meta.dirname,'..'),out=join(base,'dist');
rmSync(out,{recursive:true,force:true});mkdirSync(out,{recursive:true});
const pages=['index.html','collection.html','work.html','condition-guide.html','journal.html','about.html','finder.html','_headers'];
for(const file of pages)cpSync(join(base,file),join(out,file));
for(const f of ['assets/site.css','brand/kioku-favicon.svg','brand/kioku-lockup.svg','brand/kioku-mark.svg']){
 mkdirSync(join(out,f.split('/').slice(0,-1).join('/')),{recursive:true});cpSync(join(base,f),join(out,f));
}
for(const f of ['kioku-editorial-1.webp','kioku-editorial-2.webp','editorial-1-1.webp','editorial-1-2.webp','editorial-2-1.webp','editorial-2-2.webp']){
 const dst=join(out,'assets/img');mkdirSync(dst,{recursive:true});cpSync(join(base,'assets/img',f),join(dst,f));
}
for(const f of ['features/shared/site.js','features/catalog/records.js','features/storefront/favorites.js','features/storefront/catalog.js','features/storefront/detail.js','features/storefront/compare.js','features/discovery/finder.js','features/condition/notes.js']){
 mkdirSync(join(out,f.split('/').slice(0,-1).join('/')),{recursive:true});cpSync(join(base,f),join(out,f));
}
console.log('KIOKU V5 static frontend built: seven English pages, modular discovery, comparisons and condition notes; no transaction backend or checkout');
