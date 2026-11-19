import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const model = await readFile(new URL('../assets/models/kioku-river-guardian-v6-longform.glb', import.meta.url));
let instance = 0;

async function bootScene({ reduced = false, legacy = false, webgl = true } = {}) {
  const media = { matches: reduced };
  const subscribed = legacy ? 'addListener' : 'addEventListener';
  let mediaChange;
  media[subscribed] = (...args) => { mediaChange = args.at(-1); };

  const classes = new Set();
  const events = new Map();
  const canvasEvents = new Map();
  const frames = new Map();
  let frameId = 0;
  let draws = 0;
  const gl = new Proxy({
    NO_ERROR: 0,
    getError: () => 0,
    drawElements: () => { draws += 1; },
    getAttribLocation: () => 0,
  }, { get: (target, key) => target[key] ?? (() => true) });

  const canvas = {
    clientWidth: 390,
    clientHeight: 320,
    getContext: () => webgl ? gl : null,
    addEventListener: (type, listener) => canvasEvents.set(type, listener),
  };
  const root = {
    dataset: {},
    querySelector: () => canvas,
    classList: { add: value => classes.add(value), remove: value => classes.delete(value) },
  };
  const toggle = {
    disabled: true,
    textContent: 'Motion unavailable',
    setAttribute: (key, value) => { toggle[key] = value; },
    addEventListener: (type, listener) => events.set(type, listener),
  };

  globalThis.document = {
    hidden: false,
    querySelector: selector => selector === '[data-dragon-scene]' ? root : toggle,
    addEventListener() {},
  };
  globalThis.window = { matchMedia: () => media };
  globalThis.fetch = async () => ({
    ok: true,
    arrayBuffer: async () => model.buffer.slice(model.byteOffset, model.byteOffset + model.byteLength),
  });
  globalThis.requestAnimationFrame = callback => {
    frames.set(++frameId, callback);
    return frameId;
  };
  globalThis.cancelAnimationFrame = id => { frames.delete(id); };
  await import('../features/shared/dragon-glb-scene.js?scene=' + ++instance);
  if (webgl) {
    for (let count = 0; count < 50 && !frames.size && !reduced; count++) {
      await new Promise(resolve => setImmediate(resolve));
    }
  }

  return {
    root,
    toggle,
    classes,
    frames,
    get draws() { return draws; },
    change(value, notify = true) {
      media.matches = value;
      if (notify) mediaChange?.();
    },
    async waitForFrame() {
      for (let count = 0; count < 50 && !frames.size; count++) {
        await new Promise(resolve => setImmediate(resolve));
      }
    },
    drawFrame() {
      const [id, callback] = frames.entries().next().value;
      frames.delete(id);
      callback(id * 16);
    },
    click: () => events.get('click')(),
    loseContext: () => canvasEvents.get('webglcontextlost')({ preventDefault() {} }),
  };
}

function assertReduced(scene) {
  assert.equal(scene.root.dataset.dragonState, 'fallback');
  assert.equal(scene.classes.has('is-ready'), false);
  assert.equal(scene.toggle.textContent, 'Motion reduced');
  assert.equal(scene.toggle.disabled, true);
  assert.equal(scene.toggle['aria-pressed'], 'false');
  assert.equal(scene.frames.size, 0);
}

const delayed = await bootScene();
delayed.drawFrame();
const drawCount = delayed.draws;
delayed.change(true, false);
delayed.drawFrame();
assertReduced(delayed);
assert.equal(delayed.draws, drawCount);
delayed.change(false);
delayed.drawFrame();
assert.equal(delayed.root.dataset.dragonState, 'animated');

for (const legacy of [false, true]) {
  const scene = await bootScene({ legacy });
  scene.drawFrame();
  assert.equal(scene.root.dataset.dragonState, 'animated');
  const draws = scene.draws;
  scene.change(true);
  assertReduced(scene);
  scene.change(false);
  assert.equal(scene.toggle.disabled, true);
  scene.drawFrame();
  assert.equal(scene.root.dataset.dragonState, 'animated');
  assert.equal(scene.toggle.textContent, 'Pause motion');
  assert.equal(scene.toggle.disabled, false);
  assert.ok(scene.draws > draws);

  scene.click();
  assert.equal(scene.root.dataset.dragonState, 'paused');
  assert.equal(scene.toggle['aria-pressed'], 'true');
  assert.equal(scene.frames.size, 0);
  scene.change(true);
  assertReduced(scene);

  scene.loseContext();
  scene.change(false);
  scene.change(true);
  assert.equal(scene.toggle.textContent, 'Motion unavailable');
  assert.equal(scene.frames.size, 0);
}

const initial = await bootScene({ reduced: true });
assertReduced(initial);
initial.change(false);
await initial.waitForFrame();
initial.drawFrame();
assert.equal(initial.root.dataset.dragonState, 'animated');

const unsupported = await bootScene({ webgl: false });
assert.equal(unsupported.root.dataset.dragonState, 'fallback');
assert.equal(unsupported.toggle.disabled, true);
assert.equal(unsupported.toggle.textContent, 'Motion unavailable');

console.log('PASS: River Guardian motion preference changes, delayed/legacy events, and unavailable WebGL');
