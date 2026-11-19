const DEFAULT_DURATION = 6;

export function parseGLB(arrayBuffer) {
  const d=new DataView(arrayBuffer);
  if(d.getUint32(0,true)!==0x46546c67 || d.getUint32(4,true)!==2 ||
     d.getUint32(8,true)!==arrayBuffer.byteLength) throw new Error('Invalid GLB header');
  let json, bin, off=12;
  while(off+8<=arrayBuffer.byteLength) {
    const len=d.getUint32(off,true), type=d.getUint32(off+4,true);off+=8;
    if(off+len>arrayBuffer.byteLength)throw new Error('Truncated GLB chunk');
    if(type===0x4e4f534a)json=JSON.parse(new TextDecoder().decode(arrayBuffer.slice(off,off+len)));
    if(type===0x004e4942)bin=arrayBuffer.slice(off,off+len);
    off+=len;
  }
  if(!json?.meshes?.length || !json?.skins?.length || !json?.animations?.length || !bin)
    throw new Error('Missing GLB mesh, rig or animation');
  const components={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT4:16};
  const typed={5121:Uint8Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array};
  function accessor(index) {
    const a=json.accessors[index], view=json.bufferViews[a.bufferView];
    const T=typed[a.componentType], count=components[a.type];
    if(!T || !count || view.byteStride || a.sparse) throw new Error('Unsupported GLB accessor');
    const at=(view.byteOffset||0)+(a.byteOffset||0), end=at+a.count*count*T.BYTES_PER_ELEMENT;
    if(end>bin.byteLength)throw new Error('GLB accessor outside buffer');
    return new T(bin.slice(at,end));
  }
  const skin=json.skins[0];
  if(skin.joints.length!==10)throw new Error('River Guardian requires the 10-bone Blender rig');
  const invBind=accessor(skin.inverseBindMatrices);
  if(invBind.length!==skin.joints.length*16)throw new Error('Invalid inverse bind matrix count');
  const parentByNode=new Map();
  for(let i=0;i<json.nodes.length;i++)for(const child of json.nodes[i].children||[])parentByNode.set(child,i);
  const channels=new Map();
  for(const channel of json.animations[0].channels) {
    if(channel.target.path!=='rotation')continue;
    const sample=json.animations[0].samplers[channel.sampler];
    channels.set(channel.target.node,{time:accessor(sample.input),quat:accessor(sample.output)});
  }
  const clip=Math.max(...[...channels.values()].map(c=>c.time.at(-1)||0),DEFAULT_DURATION);
  const primitives=json.meshes[0].primitives.map(prim=>{
    const a=prim.attributes;
    if(!['POSITION','NORMAL','JOINTS_0','WEIGHTS_0'].every(key=>key in a))
      throw new Error('Incomplete skinned primitive');
    const idx=accessor(prim.indices);
    // 32-bit indices are legal in GLB, but WebGL1 needs an extension to draw them.
    // This model has under 65k vertices per part, so convert safely to Uint16.
    if(idx.length && Math.max(...idx.subarray(0,Math.min(idx.length,400)))>65535)
      throw new Error('Unsupported 32-bit mesh index');
    const position=accessor(a.POSITION), normal=accessor(a.NORMAL),
          joint=new Uint16Array(accessor(a.JOINTS_0)), weight=accessor(a.WEIGHTS_0);
    const n=position.length/3;
    if(n>65535)throw new Error('Single part too large for WebGL1');
    let tint=json.materials?.[prim.material]?.pbrMetallicRoughness?.baseColorFactor||[0.31,0.48,0.67,1];
    return {position,normal,joint,weight,indices:new Uint16Array(idx),tint};
  });
  if(primitives.length!==6)throw new Error('Expected six Blender material parts');
  return {json,accessor,primitives,invBind,joints:skin.joints,parentByNode,channels,clip};
}
