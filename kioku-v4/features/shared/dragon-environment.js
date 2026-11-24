// KIOKU Round-35 Dual-Realm 3D Environment
// Reproduces Round-35 Underwater (f394), Surface Crossing (f400), and Celestial Sky (f440) realms.

export function createDragonEnvironment(THREE, scene) {
  const root = new THREE.Group();
  root.name = 'KIOKU_DualRealmEnvironment';
  scene.add(root);

  // Subtle equirectangular reflection texture for wet scales, eyes, and horns (zero external fetch)
  const envCanvas = document.createElement('canvas');
  envCanvas.width = 256;
  envCanvas.height = 128;
  const ctx = envCanvas.getContext('2d');
  if (ctx) {
    const grad = ctx.createLinearGradient(0, 0, 0, 128);
    grad.addColorStop(0.0, '#cfe6f7');
    grad.addColorStop(0.46, '#6ea2c4');
    grad.addColorStop(0.54, '#244b6b');
    grad.addColorStop(1.0, '#091a2b');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 256, 128);
    ctx.fillStyle = 'rgba(255, 245, 225, 0.85)';
    ctx.beginPath();
    ctx.arc(178, 30, 14, 0, Math.PI * 2);
    ctx.fill();
  }
  const envTex = new THREE.CanvasTexture(envCanvas);
  envTex.mapping = THREE.EquirectangularReflectionMapping;
  envTex.colorSpace = THREE.SRGBColorSpace;
  scene.environment = envTex;
  scene.environmentIntensity = 0.65;

  // 1. Lighting Rig (interpolates Underwater cerulean shafts <-> Celestial warm sun & coral bounce)
  const hemiLight = new THREE.HemisphereLight(0x6bb8e8, 0x061a2e, 1.35);
  const keyLight = new THREE.DirectionalLight(0x8cd3ff, 2.35);
  keyLight.position.set(6.5, 9.5, 5.5);
  const rimLight = new THREE.DirectionalLight(0x63b4ff, 1.15);
  rimLight.position.set(-7.0, 4.0, -6.0);
  const coralBounce = new THREE.PointLight(0xff6b26, 0.0, 18.0, 1.6);
  coralBounce.position.set(1.2, 1.1, 1.8);
  root.add(hemiLight, keyLight, rimLight, coralBounce);

  // 2. Backdrop Atmospheric Dome (Underwater abyss <-> Surface mist <-> Celestial sky)
  const domeUniforms = {
    uRealmBlend: { value: 0.0 },
    uSubmerged: { value: 1.0 },
    uCoralLight: { value: 0.0 },
  };
  const domeMat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: domeUniforms,
    vertexShader: `
      varying vec3 vDir;
      void main() {
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uRealmBlend;
      uniform float uSubmerged;
      uniform float uCoralLight;
      varying vec3 vDir;
      void main() {
        float h = clamp(vDir.y * 0.5 + 0.5, 0.0, 1.0);
        vec3 uwTop = vec3(0.035, 0.30, 0.45);
        vec3 uwMid = vec3(0.015, 0.13, 0.24);
        vec3 uwDeep = vec3(0.006, 0.045, 0.095);
        vec3 uwCol = mix(uwDeep, uwMid, smoothstep(0.15, 0.55, h));
        uwCol = mix(uwCol, uwTop, smoothstep(0.52, 0.96, h));

        vec3 surfTop = vec3(0.84, 0.89, 0.93);
        vec3 surfHor = vec3(0.56, 0.72, 0.79);
        vec3 surfSea = vec3(0.16, 0.34, 0.44);
        vec3 surfCol = mix(surfSea, surfHor, smoothstep(0.32, 0.52, h));
        surfCol = mix(surfCol, surfTop, smoothstep(0.52, 0.88, h));

        vec3 skyTop = vec3(0.80, 0.86, 0.92);
        vec3 skyHor = vec3(0.95, 0.79, 0.67);
        vec3 skyLow = vec3(0.58, 0.64, 0.72);
        vec3 skyCol = mix(skyLow, skyHor, smoothstep(0.28, 0.54, h));
        skyCol = mix(skyCol, skyTop, smoothstep(0.54, 0.92, h));
        skyCol += vec3(0.12, 0.045, 0.015) * uCoralLight * exp(-pow((h - 0.48) * 5.0, 2.0));

        vec3 waterWorld = mix(surfCol, uwCol, uSubmerged);
        vec3 col = mix(waterWorld, skyCol, uRealmBlend);
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(62, 32, 20), domeMat);
  root.add(dome);

  // 3. Underwater Suspended Depth Particles
  const particleCount = 180;
  const pPos = new Float32Array(particleCount * 3);
  for (let i = 0; i < particleCount; i++) {
    pPos[i * 3] = (Math.random() - 0.5) * 24;
    pPos[i * 3 + 1] = (Math.random() - 0.5) * 11;
    pPos[i * 3 + 2] = (Math.random() - 0.5) * 16 - 2;
  }
  const pGeo = new THREE.BufferGeometry();
  pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
  const pMat = new THREE.PointsMaterial({
    color: 0x9ce2ff,
    size: 0.065,
    transparent: true,
    opacity: 0.45,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  });
  const particles = new THREE.Points(pGeo, pMat);
  root.add(particles);

  // 4. Water Surface Plane & Breach/Dive Ripple Rings (f400 Surface Crossing)
  const waterUni = {
    uTime: { value: 0 },
    uOpacity: { value: 0.35 },
    uPulse: { value: 0.0 },
  };
  const waterMat = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
    uniforms: waterUni,
    vertexShader: `
      uniform float uTime;
      uniform float uPulse;
      varying vec2 vWUv;
      varying float vDist;
      void main() {
        vWUv = uv;
        vec3 p = position;
        float r = length(p.xz - vec2(1.2, 0.0));
        vDist = r;
        p.y += sin(p.x * 0.9 + uTime * 1.8) * 0.045 + cos(p.z * 1.1 - uTime * 1.4) * 0.04;
        p.y += sin(r * 4.2 - uTime * 5.5) * exp(-r * 0.22) * 0.14 * uPulse;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uTime;
      uniform float uOpacity;
      uniform float uPulse;
      varying float vDist;
      void main() {
        float edgeFade = 1.0 - smoothstep(10.0, 26.0, vDist);
        float ring1 = smoothstep(0.72, 0.98, sin(vDist * 3.8 - uTime * 5.2)) * exp(-vDist * 0.24) * uPulse;
        float foam = exp(-vDist * 0.48) * uPulse * 0.65 + ring1 * 0.75;
        vec3 baseWater = mix(vec3(0.24, 0.52, 0.64), vec3(0.92, 0.97, 1.0), clamp(foam, 0.0, 1.0));
        float alpha = (uOpacity * 0.45 + foam * 0.55) * edgeFade;
        gl_FragColor = vec4(baseWater, clamp(alpha, 0.0, 0.82));
      }
    `,
  });
  const waterGeo = new THREE.PlaneGeometry(54, 54, 56, 56);
  waterGeo.rotateX(-Math.PI / 2);
  const waterPlane = new THREE.Mesh(waterGeo, waterMat);
  waterPlane.position.y = 0.05;
  root.add(waterPlane);

  // 5. Soft Volumetric Celestial Cumulus Clouds (feathered radial sprites, zero hard edges)
  const cloudGroup = new THREE.Group();
  const puffCanvas = document.createElement('canvas');
  puffCanvas.width = 256;
  puffCanvas.height = 256;
  const pCtx = puffCanvas.getContext('2d');
  if (pCtx) {
    const rg = pCtx.createRadialGradient(128, 122, 12, 128, 128, 124);
    rg.addColorStop(0.0, 'rgba(255, 250, 246, 0.92)');
    rg.addColorStop(0.38, 'rgba(248, 238, 230, 0.68)');
    rg.addColorStop(0.72, 'rgba(236, 218, 206, 0.24)');
    rg.addColorStop(1.0, 'rgba(236, 218, 206, 0.0)');
    pCtx.fillStyle = rg;
    pCtx.fillRect(0, 0, 256, 256);
  }
  const puffTex = new THREE.CanvasTexture(puffCanvas);
  puffTex.colorSpace = THREE.SRGBColorSpace;
  const puffGeo = new THREE.PlaneGeometry(1, 1);
  const cloudMat = new THREE.MeshBasicMaterial({
    map: puffTex,
    color: 0xfff5ec,
    transparent: true,
    opacity: 0.0,
    depthWrite: false,
  });
  const cloudClusters = [
    { pos: [2.2, -1.55, -2.2], scale: [6.8, 3.4, 1] },
    { pos: [-2.6, -1.75, -3.4], scale: [8.4, 4.0, 1] },
    { pos: [5.4, 0.45, -5.2], scale: [7.6, 3.8, 1] },
    { pos: [-5.2, 0.65, -5.8], scale: [8.6, 4.2, 1] },
    { pos: [0.8, -2.10, 1.4], scale: [6.2, 2.6, 1] },
  ];
  for (let i = 0; i < cloudClusters.length; i++) {
    const cl = cloudClusters[i];
    const bank = new THREE.Group();
    bank.position.set(cl.pos[0], cl.pos[1], cl.pos[2]);
    bank.userData.baseX = cl.pos[0];
    for (let j = 0; j < 3; j++) {
      const puff = new THREE.Mesh(puffGeo, cloudMat);
      puff.position.set((j - 1) * cl.scale[0] * 0.26, (j % 2) * 0.32, j * 0.18);
      puff.scale.set(cl.scale[0] * (0.82 + j * 0.12), cl.scale[1] * (0.85 + (j % 2) * 0.18), 1);
      bank.add(puff);
    }
    cloudGroup.add(bank);
  }
  root.add(cloudGroup);

  const cSkyUw = new THREE.Color(0x52b6e8);
  const cSkyCoral = new THREE.Color(0xf7eadf);
  const cGndUw = new THREE.Color(0x041526);
  const cGndCoral = new THREE.Color(0xc97b52);
  const cKeyUw = new THREE.Color(0x7fd2ff);
  const cKeyCoral = new THREE.Color(0xffe1c2);

  function update(snap, elapsedSeconds) {
    const b = snap.realmBlend;
    const sub = snap.kioku_submerged;

    domeUniforms.uRealmBlend.value = b;
    domeUniforms.uSubmerged.value = sub;
    domeUniforms.uCoralLight.value = snap.kioku_fx_coral_light;

    hemiLight.color.copy(cSkyUw).lerp(cSkyCoral, b);
    hemiLight.groundColor.copy(cGndUw).lerp(cGndCoral, b);
    hemiLight.intensity = 1.25 + b * 0.45;

    keyLight.color.copy(cKeyUw).lerp(cKeyCoral, b);
    keyLight.intensity = 2.15 + b * 0.55;
    coralBounce.intensity = snap.kioku_fx_coral_light * 3.6;
    coralBounce.position.y = snap.elevation + 0.55;

    // Underwater particles drift & fade out in sky
    particles.visible = b < 0.85;
    pMat.opacity = (1.0 - b) * (0.18 + 0.38 * sub);
    particles.position.y = (elapsedSeconds * 0.12) % 1.8;
    particles.rotation.y = elapsedSeconds * 0.025;

    // Water surface visible during underwater, surface crossing, and early transform/descent
    const waterVis = Math.max(1.0 - b * 1.25, snap.surfacePulse);
    waterPlane.visible = waterVis > 0.02;
    waterUni.uTime.value = elapsedSeconds;
    waterUni.uPulse.value = snap.surfacePulse;
    waterUni.uOpacity.value = Math.max(0, Math.min(1, waterVis)) * (sub > 0.5 ? 0.42 : 0.78);
    waterPlane.position.y = sub > 0.5 ? 1.55 : -0.18;

    // Celestial clouds drift gently & warm up with coral bounce
    cloudGroup.visible = b > 0.06;
    cloudMat.opacity = Math.min(0.76, Math.max(0, (b - 0.06) / 0.65) * 0.72);
    cloudMat.color.setRGB(1.0, 0.95 - 0.04 * snap.kioku_fx_coral_light, 0.90 - 0.06 * snap.kioku_fx_coral_light);
    for (let i = 0; i < cloudGroup.children.length; i++) {
      const bank = cloudGroup.children[i];
      const drift = ((elapsedSeconds * (0.28 + i * 0.06)) % 14) - 7;
      bank.position.x = bank.userData.baseX - drift * 0.35;
    }
  }

  function dispose() {
    envTex.dispose();
    puffTex.dispose();
    dome.geometry.dispose();
    domeMat.dispose();
    pGeo.dispose();
    pMat.dispose();
    waterGeo.dispose();
    waterMat.dispose();
    puffGeo.dispose();
    cloudMat.dispose();
  }

  return { update, dispose, root };
}
