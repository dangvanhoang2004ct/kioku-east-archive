/* KIOKU River Guardian — one volumetric, skinned GLB from the owner's Blender project.
 * WebGL1, no CDN; supports the real 10-bone, 6-material, 6-second asset.
 * 2.5D PR #5 logo is a STATIC FALLBACK only, never a second animated dragon.
 */
(() => {
  'use strict';
  const root = document.querySelector('[data-dragon-scene]');
  const canvas = root?.querySelector('[data-dragon-canvas]');
  const toggle = document.querySelector('[data-dragon-motion-toggle]');
  if (!root || !canvas) return;

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = false, ready = false, visible = true, running = true;
  let frame = 0, elapsed = 0, lastFrame = 0, shown = false;
  let dragging = false, previousX = 0, previousY = 0;
  let targetYaw = -0.11, targetPitch = 0.035, yaw = targetYaw, pitch = targetPitch;
  let gl;
  const setToggle = (label, disabled) => {
    if (!toggle) return;
    toggle.textContent = label;
    toggle.disabled = disabled;
    toggle.setAttribute('aria-pressed', String(paused));
  };
  function stop() {
    if (frame) cancelAnimationFrame(frame);
    frame = 0;
    lastFrame = 0;
  }
  function fallback(reason) {
    if (reason) console.warn('KIOKU River Guardian fallback:', reason);
    running = false;
    ready = false;
    stop();
    root.classList.remove('is-ready');
    root.dataset.dragonState = 'fallback';
    setToggle('Motion unavailable', true);
  }
  try {
    gl = canvas.getContext('webgl', {
      alpha: true, antialias: true, depth: true, premultipliedAlpha: false,
      powerPreference: 'low-power'
    });
  } catch { gl = null; }
  if (!gl) { fallback('WebGL unavailable'); return; }
  let model, program, uniforms, draws = [], duration;

  const VERTEX = `precision highp float;
attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec4 a_joint;
attribute vec4 a_weight;
uniform mat4 u_bones[10];
uniform mat4 u_orbit;
uniform vec4 u_frame;
varying vec3 v_normal;
mat4 boneAt(float index) {
  mat4 result = u_bones[0];
  for (int i=1; i<10; i++) {
    if (index > float(i)-0.5) result = u_bones[i];
  }
  return result;
}
void main() {
  mat4 skin = boneAt(a_joint.x)*a_weight.x + boneAt(a_joint.y)*a_weight.y;
  vec4 p = u_orbit * skin * vec4(a_position,1.0);
  v_normal = normalize((u_orbit * skin * vec4(a_normal,0.0)).xyz);
  gl_Position = vec4((p.x-u_frame.z)*u_frame.x,
                     (p.y-u_frame.w)*u_frame.y,
                     p.z*0.045, 1.0+p.z*0.045);
}`;
  const FRAGMENT = `precision mediump float;
varying vec3 v_normal;
uniform vec3 u_tint;
void main() {
  vec3 n = normalize(v_normal);
  vec3 lightA = normalize(vec3(-0.46,0.80,0.82));
  vec3 lightB = normalize(vec3(0.54,-0.22,0.74));
  float lit = 0.46 + 0.37*max(dot(n,lightA),0.0)
                    + 0.15*max(dot(n,lightB),0.0);
  float rim = pow(1.0-abs(n.z),2.3);
  vec3 base = pow(max(u_tint,vec3(0.0)),vec3(0.4545));
  vec3 rgb = base*lit + vec3(0.062,0.10,0.16)*rim*0.48;
  gl_FragColor = vec4(rgb,1.0);
}`;
  const identity = () => new Float32Array([
    1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1
  ]);
  function multiply(a,b) {
    const out = new Float32Array(16);
    for (let col=0;col<4;col++) for(let row=0;row<4;row++) {
      let v=0;
      for (let k=0;k<4;k++) v+=a[k*4+row]*b[col*4+k];
      out[col*4+row]=v;
    }
    return out;
  }
  function transform(q,t) {
    const [x,y,z,w] = q, [tx,ty,tz] = t;
    return new Float32Array([
      1-2*(y*y+z*z),2*(x*y+z*w),2*(x*z-y*w),0,
      2*(x*y-z*w),1-2*(x*x+z*z),2*(y*z+x*w),0,
      2*(x*z+y*w),2*(y*z-x*w),1-2*(x*x+y*y),0,
      tx,ty,tz,1
    ]);
  }
  function slerp(a,b,t) {
    let cosine = a.reduce((s,x,i)=>s+x*b[i],0);
    const q = cosine < 0 ? b.map(v=>-v) : b;
    cosine = Math.abs(cosine);
    let x,y;
    if (cosine > 0.9995) { x=1-t; y=t; }
    else {
      const angle = Math.acos(Math.min(1,cosine)), s=Math.sin(angle);
      x=Math.sin((1-t)*angle)/s; y=Math.sin(t*angle)/s;
    }
    const v=a.map((n,i)=>x*n+y*q[i]);
    const norm=Math.hypot(...v)||1;
    return v.map(n=>n/norm);
  }
  function shader(type,src) {
    const obj=gl.createShader(type);gl.shaderSource(obj,src);gl.compileShader(obj);
    if(!gl.getShaderParameter(obj,gl.COMPILE_STATUS))
      throw new Error(gl.getShaderInfoLog(obj)||'Shader compilation failed');
    return obj;
  }
  function configure(data) {
    const vs=shader(gl.VERTEX_SHADER,VERTEX),fs=shader(gl.FRAGMENT_SHADER,FRAGMENT);
    program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);
    gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))
      throw new Error(gl.getProgramInfoLog(program)||'Shader link failed');
    gl.useProgram(program);
    const attrs=[['a_position','position',3,gl.FLOAT],['a_normal','normal',3,gl.FLOAT],
      ['a_joint','joint',4,gl.UNSIGNED_SHORT],['a_weight','weight',4,gl.FLOAT]];
    const locations=attrs.map(([name])=>{
      const id=gl.getAttribLocation(program,name);
      if(id<0)throw new Error('Missing attribute '+name);
      gl.enableVertexAttribArray(id);
      return id;
    });
    draws=data.primitives.map(part=>{
      const vbos=attrs.map(([,key])=>{
        const buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);
        gl.bufferData(gl.ARRAY_BUFFER,part[key],gl.STATIC_DRAW);
        return buf;
      });
      const ebo=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ebo);
      gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,part.indices,gl.STATIC_DRAW);
      return {vbos,ebo,count:part.indices.length,color:part.tint};
    });
    uniforms={bones:gl.getUniformLocation(program,'u_bones[0]'),
      orbit:gl.getUniformLocation(program,'u_orbit'),frame:gl.getUniformLocation(program,'u_frame'),
      tint:gl.getUniformLocation(program,'u_tint')};
    gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.disable(gl.BLEND);
    model={...data,attrs,locations};
    duration=data.clip;
  }
  function uploadBones(t) {
    const matrices=new Float32Array(10*16);
    const worlds=new Map();
    const compute=(id)=>{
      if(worlds.has(id))return worlds.get(id);
      const node=model.json.nodes[id],track=model.channels.get(id);
      let q=node.rotation||[0,0,0,1];
      if(track) {
        const ticks=track.time, sample=t%duration;
        let i=0;
        while(i<ticks.length-2 && ticks[i+1]<sample)i++;
        const dt=ticks[i+1]-ticks[i]||1, a=Math.max(0,Math.min(1,(sample-ticks[i])/dt));
        q=slerp(Array.from(track.quat.slice(i*4,i*4+4)),
                Array.from(track.quat.slice((i+1)*4,(i+1)*4+4)),a);
      }
      const local=transform(q,node.translation||[0,0,0]);
      const parent=model.parentByNode.get(id);
      const global=parent==null?local:multiply(compute(parent),local);
      worlds.set(id,global);
      return global;
    };
    model.joints.forEach((nodeId,index)=>{
      const inv=model.invBind.slice(index*16,index*16+16);
      matrices.set(multiply(compute(nodeId),inv),index*16);
    });
    gl.uniformMatrix4fv(uniforms.bones,false,matrices);
  }
  function start() {
    if(ready && running && !paused && !reduced.matches && visible && !document.hidden && !frame)
      frame=requestAnimationFrame(draw);
  }
  function draw(now) {
    frame=0;
    if(reduced.matches){syncMotionPreference();return;}
    if(!ready || !running || paused || document.hidden || !visible)return;
    const dt=lastFrame?Math.min(Math.max((now-lastFrame)/1000,0),0.055):0;
    lastFrame=now;elapsed+=dt;
    yaw+=(targetYaw-yaw)*(1-Math.exp(-5.0*dt));
    pitch+=(targetPitch-pitch)*(1-Math.exp(-5.0*dt));
    const width=canvas.clientWidth,height=canvas.clientHeight;
    if(!width||!height){start();return;}
    const dpr=Math.min(window.devicePixelRatio||1,width<720?1.35:1.7);
    const w=Math.round(width*dpr),h=Math.round(height*dpr);
    if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h);}
    gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.useProgram(program);
    uploadBones(elapsed);
    const y=[0,Math.sin(yaw/2),0,Math.cos(yaw/2)];
    const x=[Math.sin(pitch/2),0,0,Math.cos(pitch/2)];
    gl.uniformMatrix4fv(uniforms.orbit,false,multiply(transform(x,[0,0,0]),transform(y,[0,0,0])));
    const mobile=width<720;
    // Production River Guardian S-curve framing: centered at (-0.86, 0.02) without head/tail/horn/limb clipping.
    gl.uniform4f(uniforms.frame,2/(mobile?12.2:11.8),mobile?.45:.47,-.86,.02);
    for(const part of draws) {
      model.attrs.forEach(([,key,size,type],i)=>{
        gl.bindBuffer(gl.ARRAY_BUFFER,part.vbos[i]);
        gl.vertexAttribPointer(model.locations[i],size,type,false,0,0);
      });
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,part.ebo);
      gl.uniform3f(uniforms.tint,part.color[0],part.color[1],part.color[2]);
      gl.drawElements(gl.TRIANGLES,part.count,gl.UNSIGNED_SHORT,0);
    }
    if(gl.getError()!==gl.NO_ERROR){fallback('GPU render error');return;}
    if(!shown){shown=true;root.classList.add('is-ready');root.dataset.dragonState='animated';setToggle('Pause motion',false);}
    start();
  }
  toggle?.addEventListener('click',()=>{
    if(!ready||!running||reduced.matches)return;
    paused=!paused;
    if(paused){stop();root.dataset.dragonState='paused';setToggle('Play motion',false);}
    else{root.dataset.dragonState='animated';setToggle('Pause motion',false);start();}
  });
  canvas.addEventListener('pointerdown',e=>{
    if(!ready||reduced.matches)return;
    dragging=true;previousX=e.clientX;previousY=e.clientY;
    canvas.setPointerCapture?.(e.pointerId);
  });
  canvas.addEventListener('pointermove',e=>{
    if(!dragging)return;
    targetYaw+=(e.clientX-previousX)*0.009;
    targetPitch=Math.max(-.8,Math.min(.8,targetPitch+(e.clientY-previousY)*.006));
    previousX=e.clientX;previousY=e.clientY;
  });
  const release=()=>dragging=false;
  canvas.addEventListener('pointerup',release);
  canvas.addEventListener('pointercancel',release);
  canvas.addEventListener('keydown',e=>{
    if(e.key==='ArrowLeft')targetYaw-=.12;
    else if(e.key==='ArrowRight')targetYaw+=.12;
    else if(e.key==='ArrowUp')targetPitch=Math.max(-.8,targetPitch-.12);
    else if(e.key==='ArrowDown')targetPitch=Math.min(.8,targetPitch+.12);
    else return;
    e.preventDefault();
  });
  canvas.addEventListener('dblclick',()=>{targetYaw=-.11;targetPitch=.035;});
  if('IntersectionObserver' in window){
    new IntersectionObserver(es=>{visible=es[0]?.isIntersecting??false;visible?start():stop();},{threshold:.01}).observe(root);
  }
  function syncMotionPreference() {
    if (!running) return;
    if (reduced.matches) {
      stop();
      paused = false;
      shown = false;
      dragging = false;
      root.classList.remove('is-ready');
      root.dataset.dragonState = 'fallback';
      setToggle('Motion reduced', true);
    } else {
      start();
    }
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stop();
    else syncMotionPreference();
  });
  if (reduced.addEventListener) reduced.addEventListener('change', syncMotionPreference);
  else reduced.addListener?.(syncMotionPreference);
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();fallback('WebGL context lost');});
  syncMotionPreference();
  fetch('./assets/models/kioku-river-guardian-v6-longform.glb')
    .then(r=>{if(!r.ok)throw new Error('Model HTTP '+r.status);return r.arrayBuffer();})
    .then(async buffer=>{
      const { parseGLB } = await import('../../data/dragon-glb.js');
      if (!running) return;
      configure(parseGLB(buffer));
      ready=true;
      start();
    })
    .catch(e=>fallback(e.message));
})();