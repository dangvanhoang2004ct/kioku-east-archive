// KIOKU Round-35 Dual-Realm PBR Material & Shader Bridge
// Blends Water <-> Coral PBR textures and multi-zone groom gradients on a single dragon rig.

const CORAL_TEXTURE_MAP = {
  MAT_Web_Skin: './assets/models/textures/skin_coral_base.webp',
  MAT_Web_Jaw: './assets/models/textures/jaw_coral_base.webp',
  MAT_Web_Ventral: './assets/models/textures/ventral_coral_base.webp',
  MAT_Web_Claw: './assets/models/textures/claw_coral_base.webp',
  MAT_Web_Tuft: './assets/models/textures/tuft_coral_base.webp',
};

export async function enhanceDragonMaterials(THREE, dragonRoot, options = {}) {
  const texMapUrls = options.coralTextures || CORAL_TEXTURE_MAP;
  const loader = new THREE.TextureLoader();

  const sharedUniforms = {
    uRealmBlend: { value: 0.0 },
    uWet: { value: 1.0 },
    uSubmerged: { value: 1.0 },
    uFxEmission: { value: 1.0 },
    uFxAura: { value: 0.0 },
    uCoralLight: { value: 0.0 },
    uTime: { value: 0.0 },
  };

  // Load Coral BaseColor PBR maps in parallel (graceful fallback if offline)
  const loadedCoralMaps = {};
  await Promise.all(
    Object.entries(texMapUrls).map(
      ([matName, url]) =>
        new Promise((resolve) => {
          loader.load(
            url,
            (tex) => {
              tex.flipY = false;
              tex.colorSpace = THREE.SRGBColorSpace;
              tex.wrapS = THREE.ClampToEdgeWrapping;
              tex.wrapT = THREE.ClampToEdgeWrapping;
              loadedCoralMaps[matName] = tex;
              resolve();
            },
            undefined,
            () => resolve()
          );
        })
    )
  );

  const skyFxMeshes = [];
  const processedMaterials = new Set();

  dragonRoot.traverse((node) => {
    if (!node.isMesh) return;
    node.frustumCulled = false;

    if (node.name.includes('Sky_ManeFlameRibbons') || node.name.includes('Sky_AuraHalo')) {
      skyFxMeshes.push(node);
    }

    const mats = Array.isArray(node.material) ? node.material : [node.material];
    for (const mat of mats) {
      if (!mat || processedMaterials.has(mat)) continue;
      processedMaterials.add(mat);
      configureMaterial(THREE, mat, sharedUniforms, loadedCoralMaps[mat.name]);
    }
  });

  function update(realmSnap, elapsedSeconds) {
    sharedUniforms.uRealmBlend.value = realmSnap.realmBlend;
    sharedUniforms.uWet.value = realmSnap.kioku_wet;
    sharedUniforms.uSubmerged.value = realmSnap.kioku_submerged;
    sharedUniforms.uFxEmission.value = realmSnap.kioku_fx_emission;
    sharedUniforms.uFxAura.value = realmSnap.kioku_fx_aura;
    sharedUniforms.uCoralLight.value = realmSnap.kioku_fx_coral_light;
    sharedUniforms.uTime.value = elapsedSeconds;

    const showSkyFx = realmSnap.kioku_fx_aura > 0.015;
    for (const fxMesh of skyFxMeshes) {
      fxMesh.visible = showSkyFx;
    }
  }

  function dispose() {
    for (const tex of Object.values(loadedCoralMaps)) {
      tex.dispose();
    }
  }

  return { update, dispose, uniforms: sharedUniforms };
}

function configureMaterial(THREE, mat, shared, coralTex) {
  const name = mat.name || '';

  // 1. Eye Inner (Golden-amber slit iris luminance) & Glossy Cornea
  if (name === 'MAT_Web_EyeInner') {
    mat.roughness = 0.08;
    mat.emissive = new THREE.Color(0xff9e2c);
    mat.emissiveMap = mat.map || null;
    mat.emissiveIntensity = 0.30;
    return;
  }
  if (name === 'MAT_Web_EyeCornea') {
    mat.transparent = true;
    mat.opacity = 0.18;
    mat.roughness = 0.02;
    mat.metalness = 0.0;
    mat.depthWrite = false;
    return;
  }

  // 2. Sky FX Ribbons & Aura Halo (Controlled Coral Flight energy)
  if (name === 'MAT_Web_FlameRibbon' || name === 'MAT_Web_AuraHalo') {
    const isRibbon = name === 'MAT_Web_FlameRibbon';
    mat.color = new THREE.Color(isRibbon ? 0xd9410d : 0xe86220);
    mat.transparent = true;
    mat.depthWrite = false;
    mat.side = THREE.DoubleSide;
    mat.blending = THREE.AdditiveBlending;
    mat.emissive = new THREE.Color(isRibbon ? 0xc83a08 : 0xd45818);
    mat.emissiveIntensity = isRibbon ? 0.42 : 0.24;
    mat.onBeforeCompile = (shader) => {
      Object.assign(shader.uniforms, shared);
      shader.vertexShader = shader.vertexShader
        .replace('#include <common>', '#include <common>\nvarying vec2 vFxUv;')
        .replace('#include <uv_vertex>', '#include <uv_vertex>\nvFxUv = uv;');
      shader.fragmentShader = shader.fragmentShader
        .replace('#include <common>', '#include <common>\nuniform float uFxAura;\nuniform float uTime;\nvarying vec2 vFxUv;')
        .replace(
          '#include <alphatest_fragment>',
          `#include <alphatest_fragment>
          float wave = 0.62 + 0.38 * sin(vFxUv.x * 16.0 - uTime * 5.2 + vFxUv.y * 4.0);
          float taper = smoothstep(0.0, 0.22, vFxUv.x) * (1.0 - smoothstep(0.45, 1.0, vFxUv.x));
          float crossFade = sin(clamp(vFxUv.y, 0.0, 1.0) * 3.14159);
          diffuseColor.a *= uFxAura * wave * taper * (0.25 + 0.45 * crossFade) * 0.46;`
        );
    };
    mat.customProgramCacheKey = () => 'kioku-skyfx-v2-' + name;
    return;
  }

  // 3. Multi-Zone Groom Material (COLOR_0 = Water, UV0.xy + UV1.x = Coral, UV1.y = groom_u)
  if (name === 'MAT_Web_Groom') {
    mat.roughness = 0.45;
    mat.metalness = 0.02;
    mat.side = THREE.DoubleSide;
    mat.onBeforeCompile = (shader) => {
      Object.assign(shader.uniforms, shared);
      shader.vertexShader = shader.vertexShader
        .replace(
          '#include <common>',
          `#include <common>
          attribute vec2 uv1;
          varying vec3 vCoralGroom;
          varying float vGroomU;`
        )
        .replace(
          '#include <begin_vertex>',
          `#include <begin_vertex>
          vCoralGroom = vec3(uv.x, uv.y, uv1.x);
          vGroomU = uv1.y;`
        );
      shader.fragmentShader = shader.fragmentShader
        .replace(
          '#include <common>',
          `#include <common>
          uniform float uRealmBlend;
          uniform float uWet;
          uniform float uFxAura;
          uniform float uFxEmission;
          varying vec3 vCoralGroom;
          varying float vGroomU;`
        )
        .replace(
          '#include <color_fragment>',
          `#include <color_fragment>
          diffuseColor.rgb = mix(diffuseColor.rgb, vCoralGroom, uRealmBlend);
          diffuseColor.rgb *= mix(1.0, 0.86, uWet * 0.55);`
        )
        .replace(
          '#include <roughnessmap_fragment>',
          `#include <roughnessmap_fragment>
          roughnessFactor = mix(roughnessFactor, 0.24, uWet * 0.55);`
        )
        .replace(
          '#include <emissivemap_fragment>',
          `#include <emissivemap_fragment>
          float tipGlow = smoothstep(0.50, 1.0, vGroomU) * uFxAura * uFxEmission * uRealmBlend;
          totalEmissiveRadiance += vec3(0.38, 0.11, 0.02) * tipGlow;`
        );
    };
    mat.customProgramCacheKey = () => 'kioku-groom-dual';
    return;
  }

  // 4. Textured Dual-Realm Scale, Ventral, Jaw, Horn, Claw, and TailTuft Materials
  mat.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, shared, {
      uCoralMap: { value: coralTex || null },
      uHasCoralMap: { value: coralTex ? 1.0 : 0.0 },
    });
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vWorldPos;\nvarying vec3 vWorldNorm;')
      .replace(
        '#include <worldpos_vertex>',
        `#include <worldpos_vertex>
        vWorldPos = (modelMatrix * vec4(transformed, 1.0)).xyz;
        vWorldNorm = normalize(mat3(modelMatrix) * objectNormal);`
      );
    shader.fragmentShader = shader.fragmentShader
      .replace(
        '#include <common>',
        `#include <common>
        uniform sampler2D uCoralMap;
        uniform float uHasCoralMap;
        uniform float uRealmBlend;
        uniform float uWet;
        uniform float uSubmerged;
        uniform float uCoralLight;
        uniform float uTime;
        varying vec3 vWorldPos;
        varying vec3 vWorldNorm;`
      )
      .replace(
        '#include <map_fragment>',
        `#include <map_fragment>
        #ifdef USE_MAP
          if (uHasCoralMap > 0.5) {
            vec4 coralSample = texture2D(uCoralMap, vMapUv);
            diffuseColor.rgb = mix(diffuseColor.rgb, coralSample.rgb, uRealmBlend);
          }
        #endif
        diffuseColor.rgb *= mix(1.0, 0.88, uWet * 0.45);`
      )
      .replace(
        '#include <roughnessmap_fragment>',
        `#include <roughnessmap_fragment>
        roughnessFactor = mix(roughnessFactor, max(0.10, roughnessFactor * 0.55), uWet * 0.72);`
      )
      .replace(
        '#include <emissivemap_fragment>',
        `#include <emissivemap_fragment>
        float caustics = sin(vWorldPos.x * 3.4 + uTime * 2.1) * cos(vWorldPos.z * 3.8 - uTime * 1.7);
        caustics = smoothstep(0.15, 0.95, caustics * 0.5 + 0.5) * max(0.0, vWorldNorm.y);
        totalEmissiveRadiance += vec3(0.05, 0.16, 0.25) * caustics * uSubmerged * (1.0 - uRealmBlend);
        float coralRim = pow(1.0 - abs(vWorldNorm.y), 2.0) * uCoralLight * uRealmBlend;
        totalEmissiveRadiance += vec3(0.22, 0.065, 0.015) * coralRim;`
      );
  };
  mat.customProgramCacheKey = () => 'kioku-pbr-' + name + (coralTex ? '-dual' : '-single');
}
