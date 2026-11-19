# KIOKU River Guardian V5 Backfix — PREVIEW ONLY

Generated 2026-11-18 from the **exact V4 GLB committed in PR #8**; kept V4 asset unchanged for comparison and rollback.

## Scope
- New `assets/models/kioku-river-guardian-v5-backfix-review.glb` is a volumetric, rigged GLB. One mesh, six material primitives, ten bones, nine rotation tracks, 6-second seamless loop.
- Rest-spine peak lowered from 1.186713 to 0.727 units. Original V4 mesh vertices, normals, inverse-bind matrices and animation tracks have been retargeted using the same PCHIP and traveling-wave method as the user review V5.
- Offline comparison against the ChatGPT V5 review artifact: position components differ by at most ~1.2e-7 units, quaternion animation is identical, normals differ at most ~1.8e-5 due to floating-point accumulation. Thus this is visually equivalent to the approved-for-preview backfix, not a different dragon.
- `features/shared/dragon-glb-scene.js` switches the requested model to V5; other UI remains unchanged.

## Release QA
- Container/glTF structural inspection of the V5 source on ChatGPT: passed (12,362 vertices, 20,064 triangles, 10 joints, 6 materials, 9 tracks).
- Cloudflare Pages build/Preview and `node scripts/validate-rig.mjs` must pass on the committed asset.
- Real Safari/Chromium WebGL rendering, GPU animation, pause/resume, keyboard/pointer orbit, reduced-motion, mobile CTA and visual likeness: **NOT VERIFIED**. Owner review required.
- No Blender project edited, no Mac Blender import claimed, no Production deployment. Do not merge into `main` without owner approval.
