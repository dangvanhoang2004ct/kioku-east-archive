/*
 * KIOKU dragon study — original procedural 3D sculpture.
 * Local WebGL geometry, no external models, scripts, telemetry or dependencies.
 * Decorative: no product or authenticity claims.
 */
(() => {
  const root = document.querySelector('[data-dragon-scene]');
  const canvas = root?.querySelector('[data-dragon-canvas]');
  if (!root || !canvas) return;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (reducedMotion.matches) return;

  let gl;
  try { gl = canvas.getContext('webgl', { alpha: true, antialias: true, depth: true, powerPreference: 'low-power' }); }
  catch { return; }
  if (!gl) return;

  const vertexShader = [
    'attribute vec3 a_position;',
    'attribute vec3 a_normal;',
    'attribute vec3 a_color;',
    'uniform float u_time, u_yaw, u_pitch, u_aspect;',
    'varying vec3 v_color, v_normal;',
    'void main(){',
    '  vec3 p=a_position;',
    '  // A traveling body ripple, strongest at the tail. Head and horns stay composed.',
    '  float tail=clamp((3.06-p.x)/5.86,0.0,1.0);',
    '  float envelope=tail*tail*(3.0-2.0*tail);',
    '  float phase=u_time*0.90-tail*7.6;',
    '  float bendY=0.083*sin(phase)+0.016*sin(phase*1.5+0.8);',
    '  float bendZ=0.108*cos(phase*0.86+0.55);',
    '  float dEnvDx=-6.0*tail*(1.0-tail)/5.86;',
    '  float dPhaseDx=7.6/5.86;',
    '  float slopeY=dEnvDx*bendY+envelope*(0.083*cos(phase)+0.024*cos(phase*1.5+0.8))*dPhaseDx;',
    '  float slopeZ=dEnvDx*bendZ-envelope*0.09288*sin(phase*0.86+0.55)*dPhaseDx;',
    '  p.y+=envelope*bendY+0.011*sin(u_time*0.56);',
    '  p.z+=envelope*bendZ;',
    '  vec3 deformedNormal=normalize(vec3(a_normal.x-slopeY*a_normal.y-slopeZ*a_normal.z,a_normal.y,a_normal.z));',
    '  float cy=cos(u_yaw),sy=sin(u_yaw),cx=cos(u_pitch),sx=sin(u_pitch);',
    '  mat3 ry=mat3(cy,0.,-sy,0.,1.,0.,sy,0.,cy);',
    '  mat3 rx=mat3(1.,0.,0.,0.,cx,sx,0.,-sx,cx);',
    '  mat3 rotation=rx*ry;',
    '  p=rotation*p;',
    '  v_normal=normalize(rotation*deformedNormal);',
    '  v_color=a_color;',
    '  float scale=4.0/max(1.7,u_aspect);',
    '  gl_Position=vec4(p.x*scale,p.y*4.0,-p.z*0.5,7.4-p.z);',
    '}'
  ].join('\n');
  const fragmentShader = [
    'precision mediump float;',
    'varying vec3 v_color,v_normal;',
    'void main(){',
    ' vec3 n=normalize(v_normal);',
    ' vec3 light=normalize(vec3(-0.46,0.78,0.92));',
    ' float diffuse=max(dot(n,light),0.);',
    ' float rim=pow(1.-abs(dot(n,vec3(0.,0.,1.))),2.2);',
    ' vec3 lit=v_color*(0.30+diffuse*0.69)+vec3(0.31,0.24,0.43)*rim*0.22;',
    ' gl_FragColor=vec4(lit,1.);',
    '}'
  ].join('\n');

  function shader(type, source) {
    const out = gl.createShader(type);
    gl.shaderSource(out, source);
    gl.compileShader(out);
    if (!gl.getShaderParameter(out, gl.COMPILE_STATUS)) {
      gl.deleteShader(out);
      throw new Error('KIOKU 3D shader could not compile');
    }
    return out;
  }

  let program;
  try {
    program = gl.createProgram();
    gl.attachShader(program, shader(gl.VERTEX_SHADER, vertexShader));
    gl.attachShader(program, shader(gl.FRAGMENT_SHADER, fragmentShader));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error('KIOKU 3D shader could not link');
  } catch {
    return; // Keep the original static dragon available.
  }

  const P = [], N = [], C = [], I = [];
  const TAU = Math.PI * 2;
  const add = (a,b) => [a[0]+b[0],a[1]+b[1],a[2]+b[2]];
  const sub = (a,b) => [a[0]-b[0],a[1]-b[1],a[2]-b[2]];
  const mul = (a,s) => [a[0]*s,a[1]*s,a[2]*s];
  const cross = (a,b) => [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
  const normal = a => { const d=Math.hypot(...a)||1; return mul(a,1/d); };
  function vertex(p,n,c) { const index=P.length/3; P.push(...p);N.push(...n);C.push(...c); return index; }
  function triangle(a,b,c,color) {
    const n=normal(cross(sub(b,a),sub(c,a)));
    const k=vertex(a,n,color),j=vertex(b,n,color),i=vertex(c,n,color);
    I.push(k,j,i);
  }

  function tube(curve, count, sides, radius, tint) {
    const first=P.length/3;
    for(let i=0;i<=count;i++){
      const t=i/count;
      const point=curve(t);
      const tangent=normal(sub(curve(Math.min(1,t+.002)),curve(Math.max(0,t-.002))));
      const tangentSide=normal(cross(tangent,[0,0,1]));
      const tangentUp=normal(cross(tangentSide,tangent));
      for(let j=0;j<=sides;j++){
        const angle=TAU*j/sides;
        const norm=normal(add(mul(tangentSide,Math.cos(angle)),mul(tangentUp,Math.sin(angle))));
        const r=radius(t);
        vertex(add(point,mul(norm,r)),norm,tint(t,angle));
      }
    }
    const stride=sides+1;
    for(let i=0;i<count;i++)for(let j=0;j<sides;j++){
      const a=first+i*stride+j,b=a+stride;
      I.push(a,b,a+1,b,b+1,a+1);
    }
  }

  // A long, tapered Japanese-style dragon rather than a rigid mascot cutout.
  const body = t => [
    -2.8+5.55*t,
    0.17*Math.sin(t*TAU*1.8+0.35)+0.28*Math.sin(t*TAU*0.83-0.6),
    0.28*Math.sin(t*TAU*1.25+0.9)
  ];
  const jade=[0.47,0.44,0.72], lavender=[0.72,0.62,0.89], bronze=[0.67,0.52,0.37];
  const shade=(a,b,t)=>a.map((v,i)=>v*(1-t)+b[i]*t);
  tube(body,116,14,t=>.065+.135*Math.pow(Math.sin(Math.PI*(.12+.80*t)),.7),
    (t,a)=>shade(jade,lavender,.30+.33*Math.sin(t*TAU*1.3)+.10*Math.sin(a*3)));
  // Narrow crest, placed along the spine so it reads as a figure in perspective.
  for(let i=7;i<102;i+=5){
    const t=i/116,pt=body(t),nxt=body(Math.min(.995,t+.025));
    const lift=[0,.18+.04*Math.sin(i),.07];
    triangle(add(pt,[0,.09,.09]),add(nxt,[0,.09,.07]),add(pt,lift),bronze);
    triangle(add(nxt,[0,.09,.07]),add(pt,[0,.09,.09]),add(pt,lift),jade);
  }

  function ellipsoid(center,radii,color,rings=12,segments=18){
    const start=P.length/3;
    for(let i=0;i<=rings;i++){
      const theta=Math.PI*i/rings;
      for(let j=0;j<=segments;j++){
        const phi=TAU*j/segments;
        const n=[Math.sin(theta)*Math.cos(phi),Math.cos(theta),Math.sin(theta)*Math.sin(phi)];
        const p=add(center,n.map((x,k)=>x*radii[k]));
        vertex(p,normal(n.map((x,k)=>x/radii[k])),color);
      }
    }
    for(let i=0;i<rings;i++)for(let j=0;j<segments;j++){
      const a=start+i*(segments+1)+j,b=a+segments+1;
      I.push(a,b,a+1,b,b+1,a+1);
    }
  }

  const head=add(body(1),[.16,.07,.04]);
  ellipsoid(head,[.33,.235,.225],lavender);
  ellipsoid(add(head,[.27,-.085,.04]),[.26,.105,.14],shade(jade,lavender,.45));
  // Horns and trailing whiskers are independently curved 3D tubes.
  for(const side of [-1,1]){
    tube(t=>add(head,[-.12-.24*t,.18+.32*t-.12*t*t,side*(.11+.14*t)]),
      18,7,t=>.065*(1-t)+.008,()=>bronze);
    tube(t=>add(head,[.18-.62*t,-.06-.22*Math.sin(Math.PI*t),side*(.13+.27*t)]),
      22,6,t=>.019*(1-t)+.003,()=>lavender);
    ellipsoid(add(head,[.12,.075,side*.185]),[.035,.034,.028],bronze,7,10);
  }
  // The tail ends in a light fan, not a product/figure image.
  for(const side of [-1,1]){
    triangle(add(body(0),[0,0,.05]),add(body(0),[-.30,side*.29,.06]),
      add(body(.035),[-.09,side*.12,.11]),shade(jade,bronze,.42));
  }

  const packed = new Float32Array(P.length*3);
  for(let i=0;i<P.length/3;i++){
    for(let k=0;k<3;k++){packed[i*9+k]=P[i*3+k];packed[i*9+3+k]=N[i*3+k];packed[i*9+6+k]=C[i*3+k];}
  }
  if(P.length/3>65535) return;
  const vertexBuffer=gl.createBuffer(),indexBuffer=gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER,vertexBuffer);
  gl.bufferData(gl.ARRAY_BUFFER,packed,gl.STATIC_DRAW);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);
  gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(I),gl.STATIC_DRAW);
  gl.useProgram(program);
  const stride=9*4;
  for(const [name,offset] of [['a_position',0],['a_normal',12],['a_color',24]]){
    const loc=gl.getAttribLocation(program,name);
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc,3,gl.FLOAT,false,stride,offset);
  }

  const uniforms={
    time:gl.getUniformLocation(program,'u_time'),
    yaw:gl.getUniformLocation(program,'u_yaw'),
    pitch:gl.getUniformLocation(program,'u_pitch'),
    aspect:gl.getUniformLocation(program,'u_aspect')
  };
  let targetX=0,targetY=0,mouseX=0,mouseY=0,frame=0,active=true;
  let visible=true,start=performance.now();
  function resize(){
    const w=canvas.clientWidth,h=canvas.clientHeight;
    if(!w||!h)return;
    const dpr=Math.min(window.devicePixelRatio||1,1.6);
    canvas.width=Math.round(w*dpr);
    canvas.height=Math.round(h*dpr);
    gl.viewport(0,0,canvas.width,canvas.height);
  }
  function draw(now){
    if(!active||!visible||document.hidden||reducedMotion.matches){frame=0;return;}
    resizeIfNeeded();
    mouseX+=(targetX-mouseX)*.035;mouseY+=(targetY-mouseY)*.035;
    const time=(now-start)/1000;
    gl.clearColor(0,0,0,0);
    gl.enable(gl.DEPTH_TEST);
    gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.uniform1f(uniforms.time,time);
    gl.uniform1f(uniforms.yaw,Math.sin(time*.24)*.28+mouseX*.34);
    gl.uniform1f(uniforms.pitch,Math.sin(time*.17)*.08+mouseY*.16);
    gl.uniform1f(uniforms.aspect,canvas.clientWidth/Math.max(1,canvas.clientHeight));
    gl.drawElements(gl.TRIANGLES,I.length,gl.UNSIGNED_SHORT,0);
    // Reveal the 3D canvas only after a successful render. Otherwise keep the still.
    if(gl.getError()!==gl.NO_ERROR){
      active=false;
      frame=0;
      root.classList.remove('is-ready');
      return;
    }
    root.classList.add('is-ready');
    frame=requestAnimationFrame(draw);
  }
  function resizeIfNeeded(){
    const dpr=Math.min(window.devicePixelRatio||1,1.6);
    if(canvas.width!==Math.round(canvas.clientWidth*dpr)||canvas.height!==Math.round(canvas.clientHeight*dpr))resize();
  }
  function startDrawing(){if(!frame&&active&&!reducedMotion.matches&&visible&&!document.hidden)frame=requestAnimationFrame(draw);}
  function stopDrawing(){if(frame)cancelAnimationFrame(frame);frame=0;}
  root.addEventListener('pointermove',e=>{
    const b=root.getBoundingClientRect();
    targetX=((e.clientX-b.left)/b.width-.5)*2;
    targetY=((e.clientY-b.top)/b.height-.5)*2;
  },{passive:true});
  root.addEventListener('pointerleave',()=>{targetX=targetY=0;});
  const observer=new IntersectionObserver(entries=>{visible=entries[0]?.isIntersecting||false;visible?startDrawing():stopDrawing();},{threshold:.01});
  observer.observe(root);
  document.addEventListener('visibilitychange',()=>{document.hidden?stopDrawing():startDrawing();});
  reducedMotion.addEventListener('change',()=>{if(reducedMotion.matches){stopDrawing();root.classList.remove('is-ready');}else{startDrawing();}});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();active=false;stopDrawing();root.classList.remove('is-ready');});
  resize();
  startDrawing();
})();
