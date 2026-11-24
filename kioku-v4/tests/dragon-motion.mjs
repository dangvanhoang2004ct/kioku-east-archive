import assert from 'node:assert/strict';
import {
  createDragonRealmState,
  sampleRound35TransitionCurve,
  JOURNEY_CYCLE_SECONDS,
} from '../features/shared/dragon-realm-state.js';

// 1. Verify Round-35 E_TransitionAction.001 curve boundary & monotonicity
const cStart = sampleRound35TransitionCurve(0);
const cMid = sampleRound35TransitionCurve(0.5);
const cEnd = sampleRound35TransitionCurve(1);
assert.equal(cStart.state, 0.0);
assert.equal(cStart.wet, 1.0);
assert.ok(cMid.state > 0.4 && cMid.state < 0.8);
assert.equal(cEnd.state, 1.0);
assert.ok(Math.abs(cEnd.wet - 0.06) < 1e-5);

// 2. Verify full continuous Dual-Realm journey cycle:
// Underwater -> Ascent -> Surface -> Transform -> Celestial Coral -> Descent -> Underwater
const state = createDragonRealmState({ initialMode: 'journey', paused: false });
const visitedPhases = new Set();
const visitedClips = new Set();
let minBlend = 1, maxBlend = 0;

for (let i = 0; i < 280; i++) {
  const snap = state.step(JOURNEY_CYCLE_SECONDS / 260);
  visitedPhases.add(snap.phaseName);
  visitedClips.add(snap.activeClip);
  minBlend = Math.min(minBlend, snap.realmBlend);
  maxBlend = Math.max(maxBlend, snap.realmBlend);
}

for (const reqPhase of ['underwater', 'ascent', 'surface', 'transform', 'celestial', 'descent']) {
  assert.ok(visitedPhases.has(reqPhase), 'Missing journey phase: ' + reqPhase);
}
for (const reqClip of ['SwimLoop', 'SurfaceCrossing', 'WaterToCoralTransform', 'CoralFlightLoop', 'CoralToWaterDescent']) {
  assert.ok(visitedClips.has(reqClip), 'Missing skeletal clip trigger: ' + reqClip);
}
assert.ok(minBlend < 0.02, 'Water realmBlend should reach ~0');
assert.ok(maxBlend > 0.98, 'Coral realmBlend should reach ~1');

// 3. Verify manual Coral / Water override transitions smoothly without snapping
state.setMode('water');
for (let i = 0; i < 40; i++) state.step(0.05);
assert.ok(state.getSnapshot().realmBlend < 0.02);

state.setMode('coral');
const firstStep = state.step(0.016);
assert.ok(firstStep.realmBlend > 0 && firstStep.realmBlend < 0.5, 'Manual Coral switch must interpolate smoothly, not snap');
for (let i = 0; i < 60; i++) state.step(0.05);
assert.ok(state.getSnapshot().realmBlend > 0.98);
assert.equal(state.getSnapshot().activeClip, 'CoralFlightLoop');

// 4. Verify explicit Pause freezes journey progression
state.setMode('journey');
state.setPaused(true);
const frozenA = state.step(0.016).phaseName;
for (let i = 0; i < 50; i++) state.step(0.2);
assert.equal(state.getSnapshot().phaseName, frozenA);
assert.equal(state.getSnapshot().paused, true);

// 5. Verify DOM fallback behavior for prefers-reduced-motion & unavailable WebGL
let sceneSeq = 0;
async function bootFallbackCheck({ reduced = false, webgl = false } = {}) {
  let mediaListener = null;
  const media = {
    matches: reduced,
    addEventListener: (_t, fn) => { mediaListener = fn; },
  };
  const classes = new Set(['is-ready']);
  const canvas = {
    clientWidth: 390,
    clientHeight: 320,
    getContext: () => (webgl ? {} : null),
    addEventListener() {},
    removeEventListener() {},
  };
  const root = {
    dataset: {},
    clientWidth: 390,
    clientHeight: 320,
    closest: () => root,
    querySelector: (sel) => (sel === '[data-dragon-canvas]' ? canvas : null),
    classList: { add: (v) => classes.add(v), remove: (v) => classes.delete(v) },
  };
  const toggle = {
    disabled: false,
    textContent: '',
    setAttribute(k, v) { this[k] = v; },
    addEventListener() {},
    removeEventListener() {},
  };
  globalThis.window = {
    location: { protocol: 'https:' },
    matchMedia: () => media,
    addEventListener() {},
    removeEventListener() {},
  };
  globalThis.document = {
    hidden: false,
    createElement: () => canvas,
    querySelector: (sel) => {
      if (sel === '[data-dragon-scene]') return root;
      if (sel === '[data-dragon-motion-toggle]') return toggle;
      return null;
    },
    querySelectorAll: () => [],
  };

  await import('../features/shared/dragon-glb-scene.js?check=' + ++sceneSeq);
  return { root, toggle, classes, triggerReduced: () => { media.matches = true; mediaListener?.(); } };
}

const red = await bootFallbackCheck({ reduced: true, webgl: true });
assert.equal(red.root.dataset.dragonState, 'fallback');
assert.equal(red.root.dataset.fallbackReason, 'reduced-motion');
assert.equal(red.toggle.textContent, 'Motion reduced');
assert.equal(red.toggle.disabled, true);
assert.equal(red.classes.has('is-ready'), false);

const noGl = await bootFallbackCheck({ reduced: false, webgl: false });
assert.equal(noGl.root.dataset.dragonState, 'fallback');
assert.equal(noGl.root.dataset.fallbackReason, 'webgl-unavailable');
assert.equal(noGl.toggle.textContent, 'Motion unavailable');
assert.equal(noGl.toggle.disabled, true);

console.log('PASS: Round-35 Dual-Realm journey, transition spline, manual override, pause precedence, and fallbacks.');
