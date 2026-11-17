import {cpSync,rmSync,mkdirSync} from 'node:fs';
import {join,resolve} from 'node:path';
const base=resolve(import.meta.dirname,'..'),out=join(base,'dist');
rmSync(out,{recursive:true,force:true});mkdirSync(out,{recursive:true});
const pages=['index.html','collection.html','work.html','condition-guide.html','journal.html','about.html','finder.html','_headers'];
for(const file of pages)cpSync(join(base,file),join(out,file));
for(const f of ['assets/site.css','brand/kioku-favicon.svg','brand/kioku-lockup.svg','brand/kioku-lockup-light.svg','brand/kioku-mark.svg']){
 mkdirSync(join(out,f.split('/').slice(0,-1).join('/')),{recursive:true});cpSync(join(base,f),join(out,f));
}
for(const asset of ['assets/img/reference-plate.svg','assets/img/kioku-dragon-flow.svg','assets/img/kioku-dragon-still.svg','assets/img/kioku-owner-dragon-logo.svg','assets/img/kioku-owner-dragon-surface.svg','assets/img/kioku-owner-dragon-texture.webp','assets/img/kioku-owner-wordmark-only.svg','assets/img/kioku-owner-logo-stage-still.svg','assets/models/kioku-river-guardian-v5-backfix-review.glb']){
 mkdirSync(join(out,asset.split('/').slice(0,-1).join('/')),{recursive:true});cpSync(join(base,asset),join(out,asset));
}
for(const f of ['features/shared/site.js','features/shared/dragon-scene.js','features/shared/dragon-glb-scene.js','features/catalog/records.js','features/storefront/favorites.js','features/storefront/catalog.js','features/storefront/detail.js','features/storefront/compare.js','features/discovery/finder.js','features/condition/notes.js']){
 mkdirSync(join(out,f.split('/').slice(0,-1).join('/')),{recursive:true});cpSync(join(base,f),join(out,f));
}
console.log('KIOKU V6 static frontend built: seven English pages, modular discovery, comparisons and condition notes; no transaction backend or checkout');
