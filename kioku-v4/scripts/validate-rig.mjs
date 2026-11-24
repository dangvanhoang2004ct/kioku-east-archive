import { readFileSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';

const root = resolve(import.meta.dirname, '..');

function parseGlbJson(filePath) {
  const buf = readFileSync(filePath);
  if (buf.toString('utf8', 0, 4) !== 'glTF' || buf.readUInt32LE(4) !== 2 || buf.readUInt32LE(8) !== buf.length) {
    throw new Error('Invalid GLB binary header: ' + filePath);
  }
  const jsonLen = buf.readUInt32LE(12);
  if (buf.toString('utf8', 16, 20) !== 'JSON') throw new Error('Missing JSON chunk: ' + filePath);
  const gltf = JSON.parse(buf.subarray(20, 20 + jsonLen).toString('utf8'));
  const binPos = 20 + jsonLen;
  if (buf.toString('utf8', binPos + 4, binPos + 8) !== 'BIN\0') throw new Error('Missing BIN chunk: ' + filePath);
  return { gltf, byteLength: buf.length };
}

// 1. Validate preserved V6 rollback asset remains intact
const rollbackPath = join(root, 'assets', 'models', 'kioku-river-guardian-v6-longform.glb');
if (!existsSync(rollbackPath)) throw new Error('Rollback River Guardian V6 GLB missing');
const rollback = parseGlbJson(rollbackPath);
if (rollback.gltf.skins?.[0]?.joints?.length !== 10) {
  throw new Error('Rollback River Guardian V6 rig corrupted');
}

// 2. Validate Production Round-35 Web GLB & Manifest
const r35Path = join(root, 'assets', 'models', 'KIOKU-Dragon-Web.glb');
const manifestPath = join(root, 'assets', 'models', 'kioku-dragon-web-manifest.json');
if (!existsSync(r35Path) || !existsSync(manifestPath)) {
  throw new Error('Round-35 Web GLB or manifest missing');
}

const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const EXPECTED_SHA = 'b766630dabd090fd9db09becb729a5d2bc269c60bd1652334e86cee0ccfecea7';
if (manifest.sourceMasterSha256 !== EXPECTED_SHA) {
  throw new Error('Round-35 manifest source SHA-256 mismatch');
}

const { gltf, byteLength } = parseGlbJson(r35Path);
if (!gltf.skins?.length || gltf.skins[0].joints.length < 70) {
  throw new Error('Expected Round-35 deform skeleton (>= 70 bones), got: ' + (gltf.skins?.[0]?.joints?.length || 0));
}

const requiredClips = ['SwimLoop', 'SurfaceCrossing', 'WaterToCoralTransform', 'CoralFlightLoop', 'CoralToWaterDescent'];
const exportedClips = new Set((gltf.animations || []).map((a) => a.name));
for (const req of requiredClips) {
  if (!exportedClips.has(req)) throw new Error('Missing required Round-35 skeletal clip: ' + req);
}

let totalVerts = 0;
let skinnedPrimitives = 0;
let hasDualGroomAttrs = false;

for (const mesh of gltf.meshes || []) {
  for (const prim of mesh.primitives || []) {
    const attrs = prim.attributes || {};
    if ('POSITION' in attrs) {
      totalVerts += gltf.accessors[attrs.POSITION].count;
    }
    if ('JOINTS_0' in attrs && 'WEIGHTS_0' in attrs) {
      skinnedPrimitives++;
    }
    if ('COLOR_0' in attrs && 'TEXCOORD_0' in attrs && 'TEXCOORD_1' in attrs) {
      hasDualGroomAttrs = true;
    }
  }
}

if (skinnedPrimitives < 10) {
  throw new Error('Expected all Round-35 anatomical meshes to be GPU-skinned, got: ' + skinnedPrimitives);
}
if (!hasDualGroomAttrs) {
  throw new Error('Dual-realm groom attributes (COLOR_0 + TEXCOORD_0 + TEXCOORD_1) missing');
}
if (totalVerts < 60000 || totalVerts > 450000) {
  throw new Error('Unexpected Round-35 optimized vertex count: ' + totalVerts);
}

for (const coralRel of Object.values(manifest.coralTextures || {})) {
  const full = resolve(root, coralRel);
  if (!existsSync(full)) throw new Error('Missing Coral PBR texture: ' + coralRel);
}

console.log(
  `Round-35 Dragon Web GLB PASS: ${totalVerts} verts, ${gltf.skins[0].joints.length} deform bones, ${exportedClips.size} clips, ${(byteLength / 1024 / 1024).toFixed(2)} MB (rollback V6 preserved).`
);
