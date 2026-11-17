# KIOKU — full-volume dragon GLB prototype

This is a **real 3D volumetric** reference model with one mesh, head and snout volumes, horns, whiskers, fins, claws, a closed body tube, and a hierarchical **11-bone skin**. The GLB includes one 8-second bone-rotation idle clip and uses vertex colors matching the owner-supplied blue/icy palette. It is **not** a flat image, a 2.5D plane, or an animated SVG.

**Quality disclaimer:** The shapes are a procedural approximation from the original KIOKU dragon illustration, not a faithful hand-sculpted Blender model. The present mesh still needs professional refinement of head/face proportions, scale pattern, underbelly plates, horns/whiskers, claws, and bone weights before Production.

## Files

- `assets/models/kioku-dragon-rig-v1.glb`: 740 KB binary GLB, approx. 9,740 vertices, 17,380 triangles, 11 bones, 8-second loop.
- `tools/generate_dragon.py`: deterministic Python source of the geometry, skin, and embedded animation; generates this GLB. Requires Python + NumPy.
- `tools/blender_refine_kioku.py`: Blender automation to import the GLB, retain the armature, save an editable `.blend` scene and export a review GLB.
- `features/shared/dragon-glb-scene.js`: WebGL 1 loader + GPU skinning, user-controlled rotation, idle playback, pause/play, accessibility and fallback. No new CDN scripts.
- `scripts/validate-rig.mjs`: verifies GLB has real geometry, skinning and animation.

## Refine in Blender

Blender was **not available** in the authoring environment, so the `.blend` script has **not been executed** and no Blender-crafted file is claimed.

In Blender, import `assets/models/kioku-dragon-rig-v1.glb` using File → Import → glTF 2.0. Inspect the armature and idle action. Replace the rough procedural surfaces in Edit/Sculpt mode and improve the material under varied lighting. Check the weighted deformation in Pose mode, especially the neck and tail.

Once visually approved, run from the `kioku-v4` working directory:

```sh
blender --background --python tools/blender_refine_kioku.py
```

This saves `assets/models/kioku-dragon-editable.blend` and `assets/models/kioku-dragon-blender-review.glb`. Both are working files; neither should be published without visual approval.

## Verification / release gate

The GLB can be parsed by trimesh and contains 11 joints and 11 animation channels. The locally available Chromium lacks a WebGL context, so the **GPU animation was not visually verified**. Browser fallback has no uncaught JS errors at 390 and 1440 widths. Do not merge this prototype into Production merely because Cloudflare Preview reports a successful build. Verify Safari/Chromium GPU animation, drag/keyboard orbit, pause/resume, reduced-motion and fallback on real hardware first.
