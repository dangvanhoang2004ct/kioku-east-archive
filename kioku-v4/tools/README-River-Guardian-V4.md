# KIOKU River Guardian V4 — review (not approved)

## Source provenance

- Direct edit of the user-provided `kioku-river-guardian-v3-review.glb` (SHA from attached file), which originates from the user's River Guardian prototype.
- Original `KIOKU-River-Guardian-Blender.blend` and Blender-compatible GLB **are actually available in this conversation**. This V4 GLB is a derived review artifact; it has **not** been imported into or exported from Blender, because Blender is unavailable in the execution container.
- Source artwork used for visual direction: user's blue dragon KIOKU logo, not image generation.

## Real V4 changes

- Removed duplicate V3 add-on whiskers and horns, keeping the base anatomy, then replaced them with layered curved, skinned cheek whiskers, brow ridges, and KIOKU-style navy/teal sweeping hair fins.
- Reduced cartoonish bulging eyes, converted eye color to pale jade; updated horn color from bronze to navy and toned down repeating dorsal spikes.
- Added sparse skinned flank-scale details and a slim trailing tail flourish, while preserving the same **six material groups** (no added material slots).
- Existing head/neck/tail/limbs preserved, with limited snout slimming and restrained 3D detail. No separate second dragon.
- The source mesh and 10-bone skin remain; every appended detail has `JOINTS_0` and `WEIGHTS_0`, so it follows existing body animation.
- Gently increased visible joint articulation through the middle body while keeping the same six-second clip with exact first/last quaternion closure.
- Removed a first test of belly seam overlays after reviewing projections because it introduced floating/stepped artifacts.

## Verified by structural and CPU projection checks

- GLB binary container, normals, vertices, indices and all six materials valid.
- 10 joints, nine animated channels, six-second loop.
- 12,362 vertices and 20,064 triangles total, about 723 KB.
- Mid-body displacement at 1.5 seconds: **0.1198** units vs V3 **0.0523** units (CPU-skinned centroid measurement, not GPU frame rate).
- Tail displacement at 1.5 seconds: **1.712** units vs V3 **0.9342** units. Larger motion is subject to subjective aesthetic review.
- Five projected views and an animated 16-frame GIF generated from real GLB triangles, **not** Blender EEVEE/Cycles or browser GPU.

## Not verified or approved

- Blender 5.3 import/export of V4, full weight paint deformation, actual GPU Safari/Chromium, and artistic likeness.
- The head/face proportions, complex secondary bones for whiskers/fins, body sculpt and leg anatomy still need meaningful manual Blender work.
- **Do not merge to Production** based on CPU screenshots/build results.

## Files

- `kioku-river-guardian-v4-review.glb` — candidate 3D asset
- `refine_kioku_v4.py` — deterministic script deriving V4 from the uploaded V3 file
- `qa_v4.py` — CPU 3D-projected QA views and motion calculation
- `KIOKU-River-Guardian-V4-6s-Swim.gif`, `KIOKU-River-Guardian-V4-QA-Contact-Sheet.png`, individual five PNG views
- `metrics-v4.json`, `qa-v4.json`