# KIOKU River Guardian — Blender-source refinement / WebGL Preview

## Source and what changed

- **Source of truth:** `KIOKU-River-Guardian-Blender.blend` supplied by the owner, built in Blender 5.3.0 on macOS (not overwritten).
- **Working GLB:** the owner's `KIOKU-River-Guardian-Blender-compatible.glb` (10 bones, 9 bone animation tracks, a seamless 6-second swim, 6 mesh/material primitives).
- **Web preview GLB:** `kioku-river-guardian-v2.glb` retains the source's exact mesh, normals, weights, skeleton, animation data, and binary buffer. The only changes in this `.glb` are PBR metallic/roughness values, a subtle eye emissive factor, and asset metadata. It is not a Blender re-export or a re-sculpt.
- **Web renderer:** adapted for **six material groups** and **10 bones** rather than the PR #6 prototype's single primitive, 11 bones and eight-second clip. Includes six material draw calls, slerped bone animation, keyboard/pointer rotation, pause, reduced-motion and non-WebGL fallback.
- **Blender enhancement script:** `refine_river_guardian_blender.py` operates on the **existing** `.blend` and saves a distinct refined `.blend` plus a review-only `.glb`. The script has not been executed in the ChatGPT environment because Blender is not installed here.

## Running the Blender script on the existing Mac

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --python tools/refine_river_guardian_blender.py -- \
  "$HOME/Downloads/KIOKU-River-Guardian-Blender.blend" \
  "$HOME/Downloads/kioku-river-refined"
```

Adjust the path above to the real location of your `.blend` file. This script preserves the original scene and adjusts only smoothing, roughness/metallic values, rig display, and six-second timeline. It will not create new horns or blindly replace the owner's art. Inspect and refine the face, horn shape, whiskers, body scales, claws, tail and deforming weights manually in Blender before any final-release GLB export.

## Release gates

1. Build and validate the `.glb` via `node scripts/validate-rig.mjs`.
2. Check 390px and 1440px responsive entry points; Collection should appear above the first fold on mobile.
3. Test real GPU rendering in Safari and Chromium, including orbit, pause/resume and `prefers-reduced-motion`.
4. Confirm the blue KIOKU dragon silhouette and animation match the owner's artwork; keep one dragon and the original wordmark.
5. Merge only when the owner approves the visual result. Production remains unchanged until then.