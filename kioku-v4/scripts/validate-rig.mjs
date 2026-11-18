import {readFileSync} from 'node:fs';
import {resolve,join} from 'node:path';
const file=join(resolve(import.meta.dirname,'..'),'assets','models','kioku-river-guardian-v6-longform.glb');
const b=readFileSync(file);
if(b.toString('utf8',0,4)!=='glTF'||b.readUInt32LE(4)!==2||b.readUInt32LE(8)!==b.length)
 throw Error('Invalid River Guardian GLB header');
const jsonLength=b.readUInt32LE(12);
if(b.toString('utf8',16,20)!=='JSON')throw Error('Missing glTF JSON chunk');
const j=JSON.parse(b.subarray(20,20+jsonLength).toString('utf8'));
if(j.skins?.length!==1||j.skins[0].joints.length!==10)
 throw Error('River Guardian needs the 10-bone Blender rig');
const anim=j.animations?.[0];
if(!anim?.name?.includes('V6 Longform'))throw Error('Expected V6 Longform 6s animation');
const rotChannels=anim?.channels?.filter(c=>c.target?.path==='rotation')||[];
if(!anim||rotChannels.length<9)throw Error('Owner 6-second 9-track animation missing');
if(j.meshes?.length!==1||j.meshes[0].primitives?.length!==6||j.materials?.length!==6)
 throw Error('Expected one owner dragon mesh split across six materials');
const components={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT4:16};
const sizes={5121:1,5123:2,5125:4,5126:4};
const binPos=20+jsonLength;
if(b.toString('utf8',binPos+4,binPos+8)!=='BIN\0')throw Error('Missing GLB binary chunk');
const binLen=b.readUInt32LE(binPos),bin= b.subarray(binPos+8,binPos+8+binLen);
function accessor(i){
 const a=j.accessors[i],v=j.bufferViews[a.bufferView];
 if(!components[a.type]||!sizes[a.componentType])throw Error('Unsupported accessor type');
 const pos=(v.byteOffset||0)+(a.byteOffset||0),bytes=a.count*components[a.type]*sizes[a.componentType];
 if(pos+bytes>bin.length)throw Error('Invalid GLB accessor bounds: '+i);
 return {a, data:bin.subarray(pos,pos+bytes)};
}
let vertices=0,triangles=0;
for(const p of j.meshes[0].primitives){
 for(const key of ['POSITION','NORMAL','JOINTS_0','WEIGHTS_0'])
  if(!(key in p.attributes))throw Error('Missing mesh attribute: '+key);
 const count=j.accessors[p.attributes.POSITION].count;
 const index=j.accessors[p.indices];
 if(count>65535)throw Error('Mesh part exceeds WebGL1 index capacity');
 if(index.type!=='SCALAR'||index.count%3!==0)throw Error('Invalid indexed triangles');
 const wg=accessor(p.attributes.WEIGHTS_0);
 if(wg.a.componentType!==5126||wg.a.type!=='VEC4')throw Error('Weights must be VEC4 float');
 const f=new Float32Array(wg.data.buffer,wg.data.byteOffset,wg.data.byteLength/4);
 for(let k=0;k<f.length;k+=4){
  const sum=f[k]+f[k+1]+f[k+2]+f[k+3];
  if(Math.abs(sum-1)>0.002)throw Error('Incorrect bone weights');
  if(f[k+2]>1e-6||f[k+3]>1e-6)throw Error('Renderer supports two weights per vertex');
 }
 vertices+=count;triangles+=index.count/3;
}
if(vertices!==25887||triangles!==43236)throw Error('Unexpected V6 Longform mesh count');
for(const c of rotChannels){
 if(c.target.path!=='rotation')throw Error('Unexpected animation target');
 const s=anim.samplers[c.sampler],ta=j.accessors[s.input],ro=j.accessors[s.output];
 if(ta.type!=='SCALAR'||ro.type!=='VEC4')throw Error('Animation accessor mismatch');
 const v=accessor(s.input).data;
 const times=new Float32Array(v.buffer,v.byteOffset,v.byteLength/4);
 if(Math.abs(times[0])>1e-4||Math.abs(times.at(-1)-6)>1e-4)
  throw Error('River Guardian should have a seamless 6-second swim');
}
const time=j.accessors[anim.samplers[0].input];
if(!Array.isArray(time.min)||!Array.isArray(time.max))
 throw Error('Blender glTF compatibility: accessor min/max must be arrays');
console.log('River Guardian V6 GLB PASS:',vertices,'vertices',triangles,'triangles; 10 bones; 6 materials; 9 rotation tracks; 6 sec.');