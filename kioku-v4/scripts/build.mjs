import { cpSync, rmSync, mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { publicPages, readPageSource } from '../data/page-source.mjs';

const base = resolve(import.meta.dirname, '..');
const out = join(base, 'dist');

rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

for (const page of publicPages) {
  writeFileSync(join(out, page), readPageSource(page));
}
cpSync(join(base, '_headers'), join(out, '_headers'));

const staticFiles = [
  'assets/site.css',
  'assets/dragon-stage.css',
  'brand/kioku-favicon.svg',
  'brand/kioku-lockup.svg',
  'brand/kioku-lockup-light.svg',
  'brand/kioku-mark.svg',
  'assets/img/reference-plate.svg',
  'assets/img/kioku-dragon-flow.svg',
  'assets/img/kioku-dragon-still.svg',
  'assets/img/kioku-owner-dragon-logo.svg',
  'assets/img/kioku-owner-dragon-surface.svg',
  'assets/img/kioku-owner-dragon-texture.webp',
  'assets/img/kioku-owner-wordmark-only.svg',
  'assets/img/kioku-owner-logo-stage-still.svg',
  'assets/img/kioku-dragon-round35-water-fallback.webp',
  'assets/img/kioku-dragon-round35-coral-fallback.webp',
  'assets/models/kioku-river-guardian-v6-longform.glb',
  'assets/models/KIOKU-Dragon-Web.glb',
  'assets/models/kioku-dragon-web-manifest.json',
  'assets/models/kioku-dragon-round35-water-fallback.webp',
  'assets/models/kioku-dragon-round35-coral-fallback.webp',
  'assets/models/textures/skin_coral_base.webp',
  'assets/models/textures/jaw_coral_base.webp',
  'assets/models/textures/ventral_coral_base.webp',
  'assets/models/textures/claw_coral_base.webp',
  'assets/models/textures/tuft_coral_base.webp',
  'assets/vendor/three.module.min.js',
  'assets/vendor/GLTFLoader.js',
  'assets/vendor/BufferGeometryUtils.js',
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
  'features/storefront/catalog.js',
  'features/storefront/detail.js',
  'features/storefront/compare.js',
  'features/discovery/finder.js',
  'features/condition/notes.js',
];

for (const rel of staticFiles) {
  const src = join(base, rel);
  if (!existsSync(src)) throw new Error('Missing build input: ' + rel);
  const dst = join(out, rel);
  mkdirSync(dirname(dst), { recursive: true });
  cpSync(src, dst);
}

console.log('KIOKU Round-35 static frontend built: 7 pages, Dual-Realm 3D Dragon GLB, and collector tools.');
