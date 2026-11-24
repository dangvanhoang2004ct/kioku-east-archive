import { readFileSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';
import { publicPages as pages, readPageSource } from '../data/page-source.mjs';

const root = resolve(import.meta.dirname, '..');
const content = (p) => readFileSync(join(root, p), 'utf8');

if (existsSync(join(root, 'design-rule.md')) && existsSync(join(root, 'design-rules.md'))) {
  const rules = content('design-rule.md');
  const pointer = content('design-rules.md');
  for (const marker of [
    '# KIOKU · Art direction & interface design rules',
    '## 8. Daily anti-AI-slop veto',
    '## 10. Japanese anime-figure focus',
    '## Project isolation — do not merge with Momo Matcha',
  ]) {
    if (!rules.includes(marker)) throw new Error('Kioku rulebook identity check failed: ' + marker);
  }
  if (/# DESIGN RULES [—-] MOMO MATCHA|momo-logo-(green|cream)|Sapo FnB PRO|Matcha Latte/i.test(rules)) {
    throw new Error('Kioku rulebook appears overwritten by Momo design rules');
  }
  if (!pointer.includes('](design-rule.md)')) {
    throw new Error('Kioku design-rules.md must redirect to canonical design-rule.md');
  }
}

const scripts = [
  'data/browser-storage.js',
  'data/dragon-glb.js',
  'features/shared/site.js',
  'features/shared/dragon-scene.js',
  'features/shared/dragon-realm-state.js',
  'features/shared/dragon-materials.js',
  'features/shared/dragon-environment.js',
  'features/shared/dragon-orbit.js',
  'features/shared/dragon-glb-scene.js',
  'features/catalog/records.js',
  'features/storefront/favorites.js',
  'features/storefront/compare.js',
  'features/storefront/catalog.js',
  'features/storefront/detail.js',
  'features/discovery/finder.js',
  'features/condition/notes.js',
];

const required = [
  ...pages.map((page) => 'pages/' + page),
  ...scripts,
  'assets/site.css',
  'assets/dragon-stage.css',
  'assets/models/kioku-river-guardian-v6-longform.glb',
  'assets/models/KIOKU-Dragon-Web.glb',
  'assets/models/kioku-dragon-web-manifest.json',
  'assets/img/kioku-dragon-round35-water-fallback.webp',
  'assets/img/kioku-dragon-round35-coral-fallback.webp',
  'assets/vendor/three.module.min.js',
  'assets/vendor/GLTFLoader.js',
  'assets/vendor/BufferGeometryUtils.js',
  'brand/kioku-favicon.svg',
  'brand/kioku-lockup.svg',
  'brand/kioku-lockup-light.svg',
  'brand/kioku-mark.svg',
  'features/inventory/verified-items.json',
];

for (const f of required) {
  if (!existsSync(join(root, f))) throw new Error('Missing project file: ' + f);
}

for (const page of pages) {
  const html = readPageSource(page);
  if (!html.includes('<html lang="en">')) throw new Error('Not English: ' + page);
  if (!html.includes('id="main"')) throw new Error('Missing main landmark: ' + page);
  if (!html.includes('data-search-dialog')) throw new Error('Missing site-wide search: ' + page);
  const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map((x) => x[1]));
  for (const [, id] of html.matchAll(/\bhref="#([^" ]+)"/g)) {
    if (!ids.has(id)) throw new Error('Broken anchor: ' + page + '#' + id);
  }
  const links = [...html.matchAll(/(?:href|src)="([^"#?]+)(?:\?[^"#]*)?(?:#[^"]*)?"/g)]
    .map((x) => x[1])
    .filter((x) => !x.startsWith('https:') && !x.startsWith('mailto:') && !x.startsWith('data:'));
  for (const link of links) {
    if (!pages.includes(link.replace(/^\.\//, '')) && !existsSync(resolve(root, link))) {
      throw new Error(`Broken path: ${page} -> ${link}`);
    }
  }
  if (/momo-matcha|sapo fnb|matcha latte/i.test(html)) {
    throw new Error('Project design contamination in ' + page);
  }
}

for (const f of scripts) execFileSync(process.execPath, ['--check', join(root, f)]);
execFileSync(process.execPath, [join(root, 'scripts/validate-inventory.mjs')]);
execFileSync(process.execPath, [join(root, 'scripts/validate-rig.mjs')], { stdio: 'inherit' });
execFileSync(process.execPath, [join(root, 'tests/dragon-motion.mjs')], { stdio: 'inherit' });

const css = content('assets/site.css');
const stageCss = content('assets/dragon-stage.css');
const home = readPageSource('index.html');

if (/hue-rotate/i.test(css) || /hue-rotate/i.test(stageCss)) {
  throw new Error('CSS hue-rotate is forbidden for Coral transformation');
}
if (!home.includes('data-dragon-scene') || !home.includes('features/shared/dragon-glb-scene.js')) {
  throw new Error('Home Round-35 3D dragon stage missing');
}
for (const ctrl of ['data-realm-select="water"', 'data-realm-select="coral"', 'data-dragon-motion-toggle', 'data-dragon-reset']) {
  if (!home.includes(ctrl)) throw new Error('Missing Home hero dragon control: ' + ctrl);
}
if (!home.includes('tabindex="0"') || !home.includes('arrow keys to rotate')) {
  throw new Error('Keyboard-accessible 3D dragon orbit missing');
}
const mobileEntry = home.match(/<div class="hero-mobile-entry shell">([\s\S]*?)<\/div>/);
if (!mobileEntry || !mobileEntry[1].includes('href="./collection.html"')) {
  throw new Error('Mobile Collection first-screen entry missing');
}
if (!css.includes('height:clamp(310px,42svh,365px)')) {
  throw new Error('Mobile dragon stage height guardrail missing');
}

const rigScene = content('features/shared/dragon-glb-scene.js') + content('features/shared/dragon-orbit.js');
for (const marker of ['KIOKU-Dragon-Web.glb', 'GLTFLoader', 'AnimationMixer', 'prefers-reduced-motion', 'webglcontextlost', 'pointermove', 'keydown']) {
  if (!rigScene.includes(marker)) throw new Error('Round-35 Three.js scene missing required feature: ' + marker);
}

const catalog = readPageSource('collection.html');
const finder = readPageSource('finder.html');
const detail = readPageSource('work.html');
const condition = readPageSource('condition-guide.html');
for (const maker of ['Bandai Spirits', 'MegaHouse']) if (!home.includes(maker)) throw new Error('Maker missing: ' + maker);
for (const prop of ['data-grid', 'data-search', 'data-maker', 'data-compare-dialog', 'data-share-search']) if (!catalog.includes(prop)) throw new Error('Catalog missing: ' + prop);
for (const prop of ['data-finder-form', 'name="maker"', 'name="style"', 'name="box"']) if (!finder.includes(prop)) throw new Error('Finder missing: ' + prop);
for (const prop of ['data-detail', 'data-lightbox']) if (!detail.includes(prop)) throw new Error('Detail missing: ' + prop);
for (const prop of ['data-condition-form', 'data-condition-output']) if (!condition.includes(prop)) throw new Error('Condition missing: ' + prop);

const records = content('features/catalog/records.js');
if (/price\s*[:=]\s*\d|stock\s*[:=]\s*\d/i.test(records)) throw new Error('Invented commercial data');
for (const page of pages) {
  if (/checkout\.html|payment-success|add.to.cart/i.test(readPageSource(page))) throw new Error('Checkout hint: ' + page);
}

console.log(`KIOKU Round-35 PASS: ${pages.length} pages, ${scripts.length} scripts, ${required.length} required files verified.`);
