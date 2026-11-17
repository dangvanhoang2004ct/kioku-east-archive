# KIOKU River Guardian V6 Longform — Preview review only

## Source and modifications
- Based directly on PR #9 V5 `kioku-river-guardian-v5-backfix-review.glb` blob `c588c844235b6b23429129a8acf632d9e4ab161e`; this is not a new dragon.
- Rebuilt from the source V5 with the same deterministic V6 longform generator delivered in ChatGPT. Target model package has the same source-derived geometry/armature/animation; differences in byte length may reflect source serialization details.
- V6 adds a long slender body/tail, restrained almond eyes and muzzle, curved branching horns, additional whiskers and dark/navy/teal details.
- New `assets/models/kioku-river-guardian-v6-longform.glb`: 15,718 vertices, 26,384 triangles; 10 bones, six material primitives, nine quaternion tracks, seamless six-second loop.
- Original V5/V4 GLBs retained for rollback; no owner's `.blend` is overwritten.

## Website changes
- WebGL model path updated in `dragon-glb-scene.js`; mobile/desktop camera horizontal view expanded from 10.7/11.7 to 16.5/16.0 with x-center -1.94; preserves Pause/Play, pointer/keyboard orbit, WebGL fallback and reduced-motion.
- Cloudflare build copies V6 GLB; check and structural rig validator refer to the new asset. Existing 7 collector pages unchanged.
- V6 frame constants are estimates; **must review using real GPU** (mobile 390x844 and desktop 1440).

## Release gate
- glTF binary shape/weight/animation checked in asset generator. Independent Python QA passed for the original review V6 package, but browser GPU was not available for the deployed artifact.
- Cloudflare Pages Preview deploy must pass. Check actual rendering, head/tail fit, joint articulation, Pause/Play, orbit, prefers-reduced-motion and static fallback on Safari and Chromium.
- The face/claws/sculpt are not identical to approved KIOKU artwork. Owner approval required.
- **NO main merge, NO Production deployment.**
