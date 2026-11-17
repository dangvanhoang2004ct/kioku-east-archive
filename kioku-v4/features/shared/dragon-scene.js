/* KIOKU: the owner's BLUE DRAGON is the texture of one animated 3D mesh.
   No separate procedural dragon; static art is fallback only. */
(() => {
  const root = document.querySelector('[data-dragon-scene]');
  const canvas = root?.querySelector('[data-dragon-canvas]');
  const motionToggle = document.querySelector('[data-dragon-motion-toggle]');
  if (!root || !canvas) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  // Do not start motion while reduced motion is on, including on first load.
  let gl;
  try { gl = canvas.getContext('webgl', {alpha:true, antialias:true, depth:true,
    premultipliedAlpha:false, powerPreference:'low-power'}); } catch { return; }
  if (!gl) return;
  const vertex = [
    'precision highp float;',
    'attribute vec2 a_uv;',
    'uniform float u_time,u_yaw,u_pitch,u_aspect;',
    'varying vec2 v_uv;',
    'varying float v_light;',
    'void main(){',
    '  v_uv=a_uv;',
    '  float tail=clamp(1.0-a_uv.x,0.0,1.0);',
    '  float influence=smoothstep(0.04,0.94,tail);',
    '  float wave=u_time*0.78-tail*7.1;',
    '  float arch=sin(a_uv.x*3.1415926)*sin(a_uv.y*3.1415926);',
    '  vec3 p=vec3((a_uv.x-0.5)*1.84,(a_uv.y-0.5)*1.84*u_aspect/2.556,0.09*arch);',
    '  p.y+=influence*(0.044*sin(wave)+0.010*sin(wave*1.6));',
    '  p.z+=influence*0.155*cos(wave*0.94+0.35);',
    '  float cy=cos(u_yaw),sy=sin(u_yaw),cp=cos(u_pitch),sp=sin(u_pitch);',
    '  vec3 turned=vec3(cy*p.x+sy*p.z,p.y,-sy*p.x+cy*p.z);',
    '  p=vec3(turned.x,cp*turned.y-sp*turned.z,sp*turned.y+cp*turned.z);',
    '  gl_Position=vec4(p.x,p.y,p.z*0.15,1.0+p.z*0.13);',
    '  v_light=0.91+0.11*arch+0.055*sin(wave+0.4);',
    '}'
  ].join('\n');
  const fragment = [
    'precision mediump float;',
    'varying vec2 v_uv;',
    'varying float v_light;',
    'uniform sampler2D u_art;',
    'void main(){',
    '  vec4 painted=texture2D(u_art,v_uv);',
    '  if(painted.a<0.005) discard;',
    '  gl_FragColor=vec4(painted.rgb*v_light,painted.a);',
    '}'
  ].join('\n');
  function makeShader(type,code){
    const shader=gl.createShader(type);gl.shaderSource(shader,code);gl.compileShader(shader);
    if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS)){
      console.warn('KIOKU 3D shader',gl.getShaderInfoLog(shader));return null;
    }
    return shader;
  }
  const vs=makeShader(gl.VERTEX_SHADER,vertex),fs=makeShader(gl.FRAGMENT_SHADER,fragment);
  if(!vs||!fs)return;
  const program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))return;
  const columns=112,rows=44,points=[],indices=[];
  for(let y=0;y<=rows;y++)for(let x=0;x<=columns;x++)points.push(x/columns,1-y/rows);
  for(let y=0;y<rows;y++)for(let x=0;x<columns;x++){
    const i=y*(columns+1)+x,j=i+columns+1;indices.push(i,j,i+1,i+1,j,j+1);
  }
  gl.bindBuffer(gl.ARRAY_BUFFER,gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(points),gl.STATIC_DRAW);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,gl.createBuffer());
  gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(indices),gl.STATIC_DRAW);
  gl.useProgram(program);
  const attr=gl.getAttribLocation(program,'a_uv');gl.enableVertexAttribArray(attr);
  gl.vertexAttribPointer(attr,2,gl.FLOAT,false,0,0);
  const U=Object.fromEntries(['time','yaw','pitch','aspect','art'].map(x=>[x,gl.getUniformLocation(program,'u_'+x)]));
  const texture=gl.createTexture();gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,texture);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
  gl.uniform1i(U.art,0);gl.enable(gl.DEPTH_TEST);gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
  let ready=false,active=true,visible=true,frame=0,targetX=0,targetY=0,mouseX=0,mouseY=0;
  let paused=false,elapsed=0,lastFrameTime=0;
  const setToggle=(label,disabled=false)=>{
    if(!motionToggle)return;
    motionToggle.textContent=label;
    motionToggle.disabled=disabled;
    motionToggle.setAttribute('aria-pressed',String(paused));
  };
  function stop(){if(frame)cancelAnimationFrame(frame);frame=0;lastFrameTime=0;}
  function start(){if(ready&&active&&visible&&!document.hidden&&!reduced.matches&&!paused&&!frame)frame=requestAnimationFrame(draw);}
  function draw(now){
    frame=0;if(!ready||!active||!visible||document.hidden||reduced.matches||paused)return;
    const w=canvas.clientWidth,h=canvas.clientHeight,dpr=Math.min(devicePixelRatio||1,innerWidth<720?1.5:1.8);
    if(!w||!h)return;
    const cw=Math.round(w*dpr),ch=Math.round(h*dpr);
    if(cw!==canvas.width||ch!==canvas.height){canvas.width=cw;canvas.height=ch;gl.viewport(0,0,cw,ch);}
    const dt=lastFrameTime?Math.min(0.05,Math.max(0,(now-lastFrameTime)/1000)):0;
    lastFrameTime=now;
    elapsed+=dt;
    const time=elapsed;
    const easing=1-Math.exp(-5.0*dt);
    mouseX+=(targetX-mouseX)*easing;mouseY+=(targetY-mouseY)*easing;
    gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.useProgram(program);gl.uniform1f(U.time,time);
    gl.uniform1f(U.yaw,Math.sin(time*0.18)*0.05+mouseX*0.10);
    gl.uniform1f(U.pitch,Math.sin(time*0.16)*0.028+mouseY*0.055);
    gl.uniform1f(U.aspect,w/h);
    gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);
    if(gl.getError()!==gl.NO_ERROR){active=false;root.classList.remove('is-ready');root.dataset.dragonState='fallback';setToggle('Motion unavailable',true);return;}
    root.classList.add('is-ready');root.dataset.dragonState='animated';setToggle('Pause motion');start();
  }
  motionToggle?.addEventListener('click',()=>{
    if(!ready||!active||reduced.matches)return;
    paused=!paused;
    if(paused){stop();root.dataset.dragonState='paused';setToggle('Play motion');}
    else {setToggle('Pause motion');start();}
  });
  root.addEventListener('pointermove',e=>{const b=root.getBoundingClientRect();targetX=((e.clientX-b.left)/b.width-.5)*2;targetY=((e.clientY-b.top)/b.height-.5)*2;},{passive:true});
  root.addEventListener('pointerleave',()=>{targetX=0;targetY=0;});
  if('IntersectionObserver' in window){new IntersectionObserver(es=>{visible=es[0]?.isIntersecting??false;visible?start():stop();},{threshold:.01}).observe(root);}
  document.addEventListener('visibilitychange',()=>document.hidden?stop():start());
  reduced.addEventListener?.('change',()=>{
    if(reduced.matches){stop();root.classList.remove('is-ready');root.dataset.dragonState='fallback';setToggle('Motion disabled',true);}
    else {paused=false;setToggle(ready?'Pause motion':'Motion unavailable',!ready);start();}
  });
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();active=false;stop();root.classList.remove('is-ready');root.dataset.dragonState='fallback';setToggle('Motion unavailable',true);});
  const art=new Image();
  art.onload=()=>{
    if(!active)return;gl.bindTexture(gl.TEXTURE_2D,texture);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,art);
    if(gl.getError()!==gl.NO_ERROR)return;
    ready=true;start();
  };
  art.onerror=()=>{root.dataset.dragonState='fallback';setToggle('Motion unavailable',true);};
  art.src='./assets/img/kioku-owner-dragon-texture.webp';
})();