/* KIOKU 3D prototype — ONE volumetric skinned dragon loaded from GLB.
   WebGL 1, no CDN, no fake AI renderer. PR #5 art remains static fallback.
   This script is deliberately standalone to keep the seven existing pages stable.
*/
(() => {
  'use strict';
  const root = document.querySelector('[data-dragon-scene]');
  const canvas = root?.querySelector('[data-dragon-canvas]');
  const toggle = document.querySelector('[data-dragon-motion-toggle]');
  if (!root || !canvas) return;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused=false;
  let gl;
  try { gl=canvas.getContext('webgl',{alpha:true,antialias:true,depth:true,premultipliedAlpha:false,powerPreference:'low-power'}); }
  catch { gl=null; }
  if (!gl) { setToggle('Motion unavailable', true); return; }
  let running=true, ready=false, loading=true, shown=false;
  let visible=true, frame=0, clock=0, previous=0;
  let drag=false, px=0, py=0, targetYaw=-0.08, targetPitch=0.02, yaw=-0.08, pitch=0.02;
  let mesh=null, skin=null, bones=null, tracks=null, duration=8;
  let buffers=[], program=null, uniforms={}, count=0;
  const DURATION = 8;
  function setToggle(label,disabled){
    if(!toggle)return;
    toggle.textContent=label;
    toggle.disabled=disabled;
    toggle.setAttribute('aria-pressed',String(paused));
  }
  function fallback(message){
    if(message)console.warn('KIOKU 3D prototype fallback:',message);
    running=false;ready=false;loading=false;stop();
    root.classList.remove('is-ready');root.dataset.dragonState='fallback';
    setToggle('Motion unavailable',true);
  }
  function stop(){if(frame)cancelAnimationFrame(frame);frame=0;previous=0;}
  function start(){if(running&&ready&&!paused&&!reduced.matches&&visible&&!document.hidden&&!frame)frame=requestAnimationFrame(draw);}
  function compile(type,source){
    const out=gl.createShader(type);gl.shaderSource(out,source);gl.compileShader(out);
    if(!gl.getShaderParameter(out,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(out)||'shader compilation failed');
    return out;
  }
  const VERTEX=`precision highp float;
attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec4 a_color;
attribute vec4 a_joint;
attribute vec4 a_weight;
uniform mat4 u_bones[11];
uniform mat4 u_orbit;
uniform vec4 u_frame;
varying vec3 v_normal;
varying vec3 v_color;
mat4 boneAt(float idx){
  mat4 result=u_bones[0];
  for(int i=1;i<11;i++){
    if(idx>float(i)-0.5)result=u_bones[i];
  }
  return result;
}
void main(){
  mat4 skin=boneAt(a_joint.x)*a_weight.x + boneAt(a_joint.y)*a_weight.y;
  vec4 p=u_orbit*(skin*vec4(a_position,1.));
  vec3 n=(u_orbit*skin*vec4(a_normal,0.)).xyz;
  v_normal=normalize(n);
  v_color=a_color.rgb;
  gl_Position=vec4((p.x-u_frame.z)*u_frame.x,p.y*u_frame.y,p.z*0.045,1.0+p.z*0.035);
}`;
  const FRAGMENT=`precision mediump float;
varying vec3 v_normal;
varying vec3 v_color;
void main(){
  vec3 n=normalize(v_normal);
  vec3 keyLight=normalize(vec3(-0.4,0.8,0.8));
  vec3 fill=normalize(vec3(0.4,-0.2,0.7));
  float light=0.52 + 0.37*max(0.,dot(n,keyLight)) + 0.13*max(0.,dot(n,fill));
  float rim=pow(1.-abs(n.z),3.0);
  vec3 rgb=v_color*light + vec3(.07,.13,.17)*rim*.55;
  gl_FragColor=vec4(rgb,1.);
}`;
  const identity=()=>new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
  function multiply(a,b){
    const o=new Float32Array(16);
    for(let c=0;c<4;c++)for(let r=0;r<4;r++){
      let sum=0;for(let k=0;k<4;k++)sum+=a[k*4+r]*b[c*4+k];
      o[c*4+r]=sum;
    }
    return o;
  }
  function transform(q,xyz){
    const [x,y,z,w]=q;const [tx,ty,tz]=xyz;
    const o=new Float32Array([
      1-2*(y*y+z*z),2*(x*y+z*w),2*(x*z-y*w),0,
      2*(x*y-z*w),1-2*(x*x+z*z),2*(y*z+x*w),0,
      2*(x*z+y*w),2*(y*z-x*w),1-2*(x*x+y*y),0,
      tx,ty,tz,1
    ]);
    return o;
  }
  function quatLerp(a,b,f){
    const dot=a[0]*b[0]+a[1]*b[1]+a[2]*b[2]+a[3]*b[3];
    const sign=dot>=0?1:-1;
    const q=a.map((v,i)=>v*(1-f)+b[i]*f*sign);
    const n=Math.hypot(...q)||1;return q.map(v=>v/n);
  }
  function readGlb(arrayBuffer){
    const dv=new DataView(arrayBuffer);
    if(dv.getUint32(0,true)!==0x46546c67||dv.getUint32(4,true)!==2||dv.getUint32(8,true)!==arrayBuffer.byteLength)
      throw new Error('Invalid glTF 2.0 binary header');
    let offset=12, json=null, bin=null;
    while(offset+8<=arrayBuffer.byteLength){
      const length=dv.getUint32(offset,true),type=dv.getUint32(offset+4,true);offset+=8;
      if(offset+length>arrayBuffer.byteLength)throw new Error('Invalid GLB chunk length');
      const chunk=arrayBuffer.slice(offset,offset+length);
      if(type===0x4e4f534a)json=JSON.parse(new TextDecoder().decode(chunk));
      if(type===0x004e4942)bin=chunk;
      offset+=length;
    }
    if(!json||!bin||!json.skins?.length||!json.animations?.length)throw new Error('GLB needs mesh, skin, and animation');
    const accessor=index=>{
      const a=json.accessors[index],v=json.bufferViews[a.bufferView];
      if(v.byteStride)throw new Error('Unsupported interleaved accessor');
      const n={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT4:16}[a.type];
      const Ty={5126:Float32Array,5123:Uint16Array,5125:Uint32Array}[a.componentType];
      if(!Ty||!n)throw new Error('Unsupported GLB accessor type');
      const at=(v.byteOffset||0)+(a.byteOffset||0),bytes=n*a.count*Ty.BYTES_PER_ELEMENT;
      if(at+bytes>bin.byteLength)throw new Error('GLB accessor exceeds buffer');
      return new Ty(bin.slice(at,at+bytes));
    };
    const prim=json.meshes[0].primitives[0];
    const data={pos:accessor(prim.attributes.POSITION),normal:accessor(prim.attributes.NORMAL),
      color:accessor(prim.attributes.COLOR_0),joint:accessor(prim.attributes.JOINTS_0),
      weight:accessor(prim.attributes.WEIGHTS_0),indices:accessor(prim.indices)};
    const bind=accessor(json.skins[0].inverseBindMatrices);
    const ids=json.skins[0].joints;
    if(ids.length!==11||bind.length!==11*16)throw new Error('Expected KIOKU 11-bone rig');
    const channelMap=new Map();const anim=json.animations[0];
    for(const ch of anim.channels){
      if(ch.target.path==='rotation'){
        const sp=anim.samplers[ch.sampler];
        channelMap.set(ch.target.node,{times:accessor(sp.input),rots:accessor(sp.output)});
      }
    }
    if(channelMap.size!==ids.length)throw new Error('Missing joint animation tracks');
    return {json,data,bind,ids,channelMap};
  }
  function configure(g){
    const vs=compile(gl.VERTEX_SHADER,VERTEX),fs=compile(gl.FRAGMENT_SHADER,FRAGMENT);
    program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);
    gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program)||'GLB renderer link failed');
    gl.useProgram(program);
    const specs=[['a_position','pos',3,gl.FLOAT],['a_normal','normal',3,gl.FLOAT],['a_color','color',4,gl.FLOAT],
      ['a_joint','joint',4,gl.UNSIGNED_SHORT],['a_weight','weight',4,gl.FLOAT]];
    for(const [name,key,size,type] of specs){
      const loc=gl.getAttribLocation(program,name);
      if(loc<0)throw new Error('Attribute not found: '+name);
      const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
      gl.bufferData(gl.ARRAY_BUFFER,g.data[key],gl.STATIC_DRAW);
      gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,size,type,false,0,0);
      buffers.push(buffer);
    }
    const indexBuffer=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,g.data.indices,gl.STATIC_DRAW);
    count=g.data.indices.length;
    uniforms={bone:gl.getUniformLocation(program,'u_bones[0]'),orbit:gl.getUniformLocation(program,'u_orbit'),
      frame:gl.getUniformLocation(program,'u_frame')};
    mesh=g;
    gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE); // model material is double-sided
    gl.disable(gl.BLEND);
    const firstTrack=g.channelMap.get(g.ids[0]);duration=firstTrack.times[firstTrack.times.length-1]||DURATION;
  }
  function updateBones(time){
    const g=mesh,joints=new Float32Array(11*16),world=[];
    for(let i=0;i<g.ids.length;i++){
      const nodeId=g.ids[i],node=g.json.nodes[nodeId],track=g.channelMap.get(nodeId);
      const ts=track.times,rots=track.rots,t=time%duration;
      let k=0;while(k<ts.length-2&&ts[k+1]<t)k++;
      const dt=ts[k+1]-ts[k]||1,f=Math.max(0,Math.min(1,(t-ts[k])/dt));
      const q=quatLerp(Array.from(rots.slice(k*4,k*4+4)),Array.from(rots.slice((k+1)*4,(k+1)*4+4)),f);
      const local=transform(q,node.translation||[0,0,0]);
      world[i]=i===0?local:multiply(world[i-1],local);
      const inv=g.bind.slice(i*16,i*16+16),skinned=multiply(world[i],inv);
      joints.set(skinned,i*16);
    }
    gl.uniformMatrix4fv(uniforms.bone,false,joints);
  }
  function draw(now){
    frame=0;if(!running||!ready||paused||reduced.matches||document.hidden||!visible)return;
    const dt=previous?Math.min((now-previous)/1000,0.055):0;previous=now;clock+=Math.max(0,dt);
    const ease=1-Math.exp(-4.6*Math.max(.005,dt));
    yaw+=(targetYaw-yaw)*ease;pitch+=(targetPitch-pitch)*ease;
    const w=canvas.clientWidth,h=canvas.clientHeight;
    if(!w||!h)return;
    const pixelRatio=Math.min(devicePixelRatio||1,w<720?1.4:1.7);
    const W=Math.round(w*pixelRatio),H=Math.round(h*pixelRatio);
    if(W!==canvas.width||H!==canvas.height){canvas.width=W;canvas.height=H;gl.viewport(0,0,W,H);}
    gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.useProgram(program);
    updateBones(clock);
    const qy=[0,Math.sin(yaw/2),0,Math.cos(yaw/2)],qx=[Math.sin(pitch/2),0,0,Math.cos(pitch/2)];
    const orbit=multiply(transform(qx,[0,0,0]),transform(qy,[0,0,0]));
    gl.uniformMatrix4fv(uniforms.orbit,false,orbit);
    const aspect=w/h,small=w<720;
    const width=small?8.9:11.75;
    gl.uniform4f(uniforms.frame,2/width,2*aspect/width,small?0.75:0.25,0);
    gl.drawElements(gl.TRIANGLES,count,gl.UNSIGNED_SHORT,0);
    if(gl.getError()!==gl.NO_ERROR){fallback('WebGL draw error');return;}
    if(!shown){shown=true;root.classList.add('is-ready');root.dataset.dragonState='animated';setToggle('Pause motion',false);}
    start();
  }
  toggle?.addEventListener('click',()=>{
    if(!ready||!running||reduced.matches)return;
    paused=!paused;
    if(paused){stop();setToggle('Play motion',false);root.dataset.dragonState='paused';}
    else {setToggle('Pause motion',false);root.dataset.dragonState='animated';start();}
  });
  canvas.addEventListener('pointerdown',e=>{
    if(!ready||reduced.matches)return;
    drag=true;px=e.clientX;py=e.clientY;canvas.setPointerCapture?.(e.pointerId);
  });
  canvas.addEventListener('pointermove',e=>{
    if(!drag)return;
    targetYaw+=(e.clientX-px)*.009;targetPitch=Math.max(-.62,Math.min(.62,targetPitch+(e.clientY-py)*.006));
    px=e.clientX;py=e.clientY;
  });
  const endDrag=()=>{drag=false;};canvas.addEventListener('pointerup',endDrag);canvas.addEventListener('pointercancel',endDrag);
  canvas.addEventListener('keydown',e=>{
    const amount=0.12;
    if(e.key==='ArrowLeft')targetYaw-=amount;
    else if(e.key==='ArrowRight')targetYaw+=amount;
    else if(e.key==='ArrowUp')targetPitch=Math.max(-.62,targetPitch-amount);
    else if(e.key==='ArrowDown')targetPitch=Math.min(.62,targetPitch+amount);
    else return;
    e.preventDefault();
  });
  canvas.addEventListener('dblclick',()=>{targetYaw=-0.08;targetPitch=0.02;});
  if('IntersectionObserver' in window){
    new IntersectionObserver(entries=>{visible=entries[0]?.isIntersecting??false;visible?start():stop();},{threshold:.01}).observe(root);
  }
  document.addEventListener('visibilitychange',()=>document.hidden?stop():start());
  reduced.addEventListener?.('change',()=>{
    if(reduced.matches){stop();root.classList.remove('is-ready');root.dataset.dragonState='fallback';setToggle('Motion reduced',true);}
    else {paused=false;shown=false;setToggle(ready?'Pause motion':'Motion unavailable',!ready);start();}
  });
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();fallback('context lost');});
  if(reduced.matches){root.dataset.dragonState='fallback';setToggle('Motion reduced',true);}
  const controller=new AbortController();
  fetch('./assets/models/kioku-dragon-rig-v1.glb',{signal:controller.signal})
    .then(response=>{if(!response.ok)throw new Error('GLB fetch '+response.status);return response.arrayBuffer();})
    .then(buffer=>{const model=readGlb(buffer);configure(model);ready=true;loading=false;start();})
    .catch(error=>fallback(error.message));
})();