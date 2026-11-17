import { readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
const file=join(resolve(import.meta.dirname,'..'),'assets/models/kioku-dragon-rig-v1.glb');
const bin=readFileSync(file);
if(bin.toString('utf8',0,4)!=='glTF'||bin.readUInt32LE(4)!==2||bin.readUInt32LE(8)!==bin.length)
  throw Error('Invalid KIOKU GLB header');
const n=bin.readUInt32LE(12);
if(bin.toString('utf8',16,20)!=='JSON')throw Error('Missing GLB JSON chunk');
const d=JSON.parse(bin.subarray(20,20+n).toString('utf8'));
if(d.skins?.length!==1||d.skins[0].joints?.length!==11)throw Error('KIOKU requires exactly 11 rig joints');
if(d.animations?.length!==1||d.animations[0].channels?.length!==11)throw Error('KIOKU idle bone animation missing');
const required=['POSITION','NORMAL','COLOR_0','JOINTS_0','WEIGHTS_0'];
const attrs=d.meshes?.[0]?.primitives?.[0]?.attributes||{};
for(const a of required)if(!(a in attrs))throw Error('Missing 3D mesh attribute: '+a);
const p=d.accessors[attrs.POSITION],i=d.accessors[d.meshes[0].primitives[0].indices];
if(p.count<5000||i.count<20000)throw Error('Unexpectedly reduced volumetric geometry');
if(d.meshes.length!==1)throw Error('KIOKU must have a single dragon mesh');
console.log('KIOKU volumetric prototype GLB valid:',p.count,'vertices',i.count/3,'triangles',d.skins[0].joints.length,'bones');
