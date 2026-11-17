import {readFileSync,existsSync} from 'node:fs';
import {join,resolve,dirname} from 'node:path';
import {execFileSync} from 'node:child_process';
const root=resolve(import.meta.dirname,'..');
const content=p=>readFileSync(join(root,p),'utf8');
const hasRulebook=existsSync(join(root,'design-rule.md'))&&existsSync(join(root,'design-rules.md'));const rules=hasRulebook?content('design-rule.md'):'';const pointer=hasRulebook?content('design-rules.md'):'';
if(existsSync(join(root,'design-rule.md'))&&existsSync(join(root,'design-rules.md'))){for(const marker of ['# KIOKU · Art direction & interface design rules','## 8. Daily anti-AI-slop veto','## 10. Japanese anime-figure focus','## Project isolation — do not merge with Momo Matcha'])if(!rules.includes(marker))throw Error('Kioku rulebook identity check failed: '+marker);}
if(/# DESIGN RULES [—-] MOMO MATCHA|momo-logo-(green|cream)|Sapo FnB PRO|Matcha Latte/i.test(rules))throw Error('Kioku rulebook appears overwritten by Momo design rules');
if(existsSync(join(root,'design-rule.md'))&&existsSync(join(root,'design-rules.md'))&&!pointer.includes('](design-rule.md)'))throw Error('Kioku design-rules.md must redirect to canonical design-rule.md');
const pages=['index.html','collection.html','finder.html','work.html','condition-guide.html','journal.html','about.html'];
const scripts=['features/shared/site.js','features/shared/dragon-scene.js','features/catalog/records.js','features/storefront/favorites.js','features/storefront/compare.js','features/storefront/catalog.js','features/storefront/detail.js','features/discovery/finder.js','features/condition/notes.js'];
const required=[...pages,...scripts,'assets/site.css','assets/img/kioku-dragon-flow.svg','assets/img/kioku-dragon-still.svg','assets/img/kioku-owner-dragon-logo.svg','assets/img/kioku-owner-dragon-surface.svg','assets/img/kioku-owner-wordmark-only.svg','assets/img/kioku-owner-logo-stage-still.svg','brand/kioku-favicon.svg','brand/kioku-lockup.svg','brand/kioku-lockup-light.svg','brand/kioku-mark.svg','features/inventory/verified-items.json'];
for(const f of required)if(!existsSync(join(root,f)))throw Error('Missing project file: '+f);
for(const page of pages){const html=content(page);if(!html.includes('<html lang="en">'))throw Error('Not English: '+page);if(!html.includes('id="main"'))throw Error('Missing main landmark: '+page);if(!html.includes('data-search-dialog'))throw Error('Missing site-wide search: '+page);const ids=new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]));for(const [,id] of html.matchAll(/\bhref="#([^" ]+)"/g))if(!ids.has(id))throw Error('Broken anchor: '+page+'#'+id);
const links=[...html.matchAll(/(?:href|src)="([^"#?]+)(?:\?[^"#]*)?(?:#[^"]*)?"/g)].map(x=>x[1]).filter(x=>!x.startsWith('https:')&&!x.startsWith('mailto:')&&!x.startsWith('data:'));
for(const link of links)if(!existsSync(resolve(dirname(join(root,page)),link)))throw Error(`Broken path: ${page} -> ${link}`);
if(/momo-matcha|sapo fnb|matcha latte/i.test(html))throw Error('Project design contamination in '+page);
}
for(const f of scripts)execFileSync(process.execPath,['--check',join(root,f)]);
execFileSync(process.execPath,[join(root,'scripts/validate-inventory.mjs')]);
const css=content('assets/site.css');
if(!css.includes('kioku-dragon-flow.svg')||!css.includes('kioku-dragon-still.svg'))throw Error('Dragon motion or reduced-motion fallback not wired into Home');
const home=content('index.html');if(!home.includes('data-dragon-scene')||!home.includes('hero-introduction'))throw Error('KIOKU Home immersive hero unavailable');
if(home.includes('hero-owner-art'))throw Error('Duplicate static dragon card must not appear outside the 3D scene');
for(const marker of ['kioku-owner-dragon-surface.svg','kioku-owner-wordmark-only.svg','kioku-owner-logo-stage-still.svg']){
 if(!content('scripts/build.mjs').includes(marker))throw Error('Unbundled owner asset: '+marker);
}
if(!home.includes('hero-dragon-wordmark')||!home.includes('kioku-owner-logo-stage-still.svg'))throw Error('Unified animated scene or fallback missing');
if(!css.includes('.home .hero-dragon.is-ready .hero-dragon-wordmark'))throw Error('Unified wordmark must be part of animated stage');
if(!home.includes('kioku-lockup-light.svg'))throw Error('Approved KIOKU header logo missing');
const dragon=content('features/shared/dragon-scene.js');
for(const marker of ['texture2D(u_art,v_uv)','float tail=clamp(1.0-a_uv.x','p.z+=influence*0.155','a_uv','data-dragon-scene','webglcontextlost','prefers-reduced-motion']){
 if(!dragon.includes(marker))throw Error('Animated textured dragon regression: '+marker);
}
if(dragon.includes('ellipsoid(')||dragon.includes('function tube('))throw Error('Old second dragon mesh must not be rendered');

const index=content('index.html'),catalog=content('collection.html'),finder=content('finder.html'),detail=content('work.html'),condition=content('condition-guide.html');
for(const maker of ['Bandai Spirits','MegaHouse'])if(!index.includes(maker))throw Error('Maker discovery missing on Home: '+maker);
for(const prop of ['data-grid','data-search','data-maker','data-compare-dialog','data-share-search'])if(!catalog.includes(prop))throw Error('Catalog feature missing: '+prop);
for(const prop of ['data-finder-form','name="maker"','name="style"','name="box"'])if(!finder.includes(prop))throw Error('Finder missing: '+prop);
for(const prop of ['data-detail','data-lightbox'])if(!detail.includes(prop))throw Error('Detail missing: '+prop);
for(const prop of ['data-condition-form','data-condition-output'])if(!condition.includes(prop))throw Error('Condition guide missing: '+prop);
const records=content('features/catalog/records.js');if(/price\s*[:=]\s*\d|stock\s*[:=]\s*\d/i.test(records))throw Error('Invented commercial data in manufacturer references');
for(const page of pages)if(/checkout\.html|payment-success|add.to.cart/i.test(content(page)))throw Error('Unverified checkout hint: '+page);
console.log(`KIOKU V6 PASS: ${pages.length} pages, ${scripts.length} feature scripts, ${required.length} required files, links, project isolation and inventory schema`);
