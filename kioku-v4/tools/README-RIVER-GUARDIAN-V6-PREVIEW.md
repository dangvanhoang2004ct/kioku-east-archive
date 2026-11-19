# KIOKU River Guardian V6 Longform — Production 3D Sculpt & Rig

## Source and Blender 5.3 modifications
- Refined directly in **Blender 5.3.0** via `tools/sculpt_river_guardian_production.py` from the existing River Guardian rigged model, using the approved 2D KIOKU dragon identity artwork as the visual source of truth.
- Editable Blender source saved at `assets/models/kioku-river-guardian-production.blend`.
- Optimized website GLB exported at `assets/models/kioku-river-guardian-v6-longform.glb`: **18,915 vertices, 34,840 triangles**; 10 bones, 6 material primitives, 9 quaternion rotation tracks, seamless 6.0-second swimming loop.
- Anatomical & artistic refinements:
  - Sculpted East Asian river dragon head (wedge cranium, concave nasal bridge, upturned snout at ~22°, bold upturned almond eyes with dark navy pupil & muted-teal/navy brow ridge, tapered teal cheek highlight, flush pale-ice lower jaw rim, 3-tuft navy chin beard).
  - Reconstructed branching stag antlers (bold Y-forked deep-navy front antler + swept muted-teal rear antler), cohesive S-curved flame mane locks hugging the skull/neck, and a single pair of calligraphy S-curved whiskers.
  - Restored true KIOKU S-curve serpentine silhouette with smooth deep-navy dorsal spine, signature dorsal neck fin, compact S-scroll ventral neck ribbon, flush segmented pale ice-blue underbelly, sculpted 3-clawed dragon forelimbs at the lower trough, and a two-pronged flame tail fin.
- Original V2/V4/V5 GLBs retained for rollback.

## Website integration
- `features/shared/dragon-glb-scene.js` converts linear RGB PBR material factors to sRGB (`pow(..., 0.4545)`) and centers framing at `(-0.86, 0.02)` with mobile/desktop horizontal span `12.2 / 11.8` and vertical scale `0.45 / 0.47` (zero clipping across all 12 steps of the 6s cycle).
- Preserves Pause/Play (`aria-pressed`), pointer & keyboard orbit, `prefers-reduced-motion` handling, WebGL fallback, mobile first-screen Collection CTA, and all 7 collector pages.

## Release gate
- glTF binary shape/weight/animation checked in asset generator. Independent Python QA passed for the original review V6 package, but browser GPU was not available for the deployed artifact.
- Cloudflare Pages Preview deploy must pass. Check actual rendering, head/tail fit, joint articulation, Pause/Play, orbit, prefers-reduced-motion and static fallback on Safari and Chromium.
- The face/claws/sculpt are not identical to approved KIOKU artwork. Owner approval required.
- **NO main merge, NO Production deployment.**
