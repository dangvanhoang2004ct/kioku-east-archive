// KIOKU Home Hero — Round-35 Real-Time Three.js Dual-Realm Dragon Scene
(() => {
  const sceneRoot = document.querySelector('[data-dragon-scene]');
  const stage = sceneRoot?.closest('.hero-stage') || sceneRoot;
  const canvas = sceneRoot ? sceneRoot.querySelector('[data-dragon-canvas]') : null;
  if (!sceneRoot || !canvas) return;

  const toggleBtn = document.querySelector('[data-dragon-motion-toggle]');
  const resetBtn = document.querySelector('[data-dragon-reset]');
  const statusEl = document.querySelector('[data-realm-status]');
  const realmBtns = Array.from(document.querySelectorAll('[data-realm-select]'));
  const fallbackImg = sceneRoot.querySelector('[data-dragon-fallback-img]');

  const motionQuery = typeof window.matchMedia === 'function'
    ? window.matchMedia('(prefers-reduced-motion: reduce)')
    : { matches: false };

  const setToggleState = (label, disabled, pressed = false) => {
    if (!toggleBtn) return;
    toggleBtn.textContent = label;
    toggleBtn.disabled = disabled;
    toggleBtn.setAttribute('aria-pressed', pressed ? 'true' : 'false');
  };

  const setExtraControlsHidden = (hidden) => {
    for (const el of [resetBtn, ...realmBtns]) {
      if (!el) continue;
      el.hidden = hidden;
      el.disabled = hidden;
    }
  };

  const activateStaticFallback = (reason) => {
    sceneRoot.dataset.dragonState = 'fallback';
    sceneRoot.dataset.fallbackReason = reason;
    sceneRoot.classList.remove('is-ready');
    setToggleState(reason === 'reduced-motion' ? 'Motion reduced' : 'Motion unavailable', true, false);
    setExtraControlsHidden(true);
    window.__KIOKU_DRAGON_DIAG__ = { mode: 'fallback', reason };
  };

  const isStandaloneSrcdoc = window.location?.protocol === 'about:' || window.location?.protocol === 'data:';
  if (isStandaloneSrcdoc || window.__KIOKU_DISABLE_WEBGL__) {
    activateStaticFallback(isStandaloneSrcdoc ? 'standalone-srcdoc' : 'webgl-disabled');
    return;
  }

  let activeCleanup = null;
  let bootToken = 0;

  async function mountWebGLScene(token) {
    if (motionQuery.matches) {
      activateStaticFallback('reduced-motion');
      return;
    }

    const probeCanvas = typeof document.createElement === 'function' ? document.createElement('canvas') : canvas;
    const probeGl = typeof probeCanvas?.getContext === 'function'
      ? (probeCanvas.getContext('webgl2') || probeCanvas.getContext('webgl'))
      : null;
    if (!probeGl) {
      activateStaticFallback('webgl-unavailable');
      return;
    }

    setToggleState('Loading 3D...', true, false);

    try {
      const [THREE, { GLTFLoader }, { createDragonRealmState }, { enhanceDragonMaterials }, { createDragonEnvironment }, { createDragonOrbitController }] =
        await Promise.all([
          import('../../assets/vendor/three.module.min.js'),
          import('../../assets/vendor/GLTFLoader.js'),
          import('./dragon-realm-state.js'),
          import('./dragon-materials.js'),
          import('./dragon-environment.js'),
          import('./dragon-orbit.js'),
        ]);
      if (token !== bootToken || motionQuery.matches) {
        if (motionQuery.matches) activateStaticFallback('reduced-motion');
        return;
      }

      const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.06;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(33, 16 / 9, 0.1, 120);
      const env = createDragonEnvironment(THREE, scene);
      const realmState = createDragonRealmState({ initialMode: 'journey', paused: false });
      const orbit = createDragonOrbitController(canvas, sceneRoot);

      const gltf = await new GLTFLoader().loadAsync('./assets/models/KIOKU-Dragon-Web.glb');
      if (token !== bootToken || motionQuery.matches) {
        orbit.dispose();
        env.dispose();
        renderer.dispose();
        if (motionQuery.matches) activateStaticFallback('reduced-motion');
        return;
      }

      const dragonPivot = new THREE.Group();
      const dragonRoot = gltf.scene;
      const box = new THREE.Box3().setFromObject(dragonRoot);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const normScale = 8.5 / Math.max(1.0, size.x, size.y, size.z);
      dragonRoot.scale.setScalar(normScale);
      dragonRoot.position.set(-center.x * normScale, -center.y * normScale, -center.z * normScale);
      dragonPivot.add(dragonRoot);
      scene.add(dragonPivot);

      const matBridge = await enhanceDragonMaterials(THREE, dragonRoot);
      const mixer = new THREE.AnimationMixer(dragonRoot);
      const actions = {};
      for (const clip of gltf.animations) {
        const act = mixer.clipAction(clip);
        act.enabled = true;
        actions[clip.name] = act;
      }
      let currentClipName = actions.SwimLoop ? 'SwimLoop' : (gltf.animations[0]?.name || '');
      actions[currentClipName]?.reset().play();

      const switchClip = (nextName) => {
        if (!nextName || nextName === currentClipName || !actions[nextName]) return;
        const prev = actions[currentClipName];
        const next = actions[nextName];
        next.reset().play();
        prev?.crossFadeTo(next, 0.55, true);
        currentClipName = nextName;
      };

      const resize = () => {
        const w = Math.max(1, sceneRoot.clientWidth || canvas.clientWidth || 390);
        const h = Math.max(1, sceneRoot.clientHeight || canvas.clientHeight || 320);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, w < 768 ? 1.5 : 2.0));
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        orbit.setViewportWidth(w, h);
        camera.updateProjectionMatrix();
      };
      resize();
      window.addEventListener?.('resize', resize);

      const syncUi = (snap) => {
        sceneRoot.dataset.dragonState = snap.paused ? 'paused' : 'animated';
        sceneRoot.dataset.realmMode = snap.mode;
        sceneRoot.dataset.realmPhase = snap.phaseName;
        if (statusEl) statusEl.textContent = snap.stageLabel;
        setToggleState(snap.paused ? 'Play motion' : 'Pause motion', false, snap.paused);
        for (const btn of realmBtns) {
          const r = btn.dataset.realmSelect;
          const active = snap.mode === r || (snap.mode === 'journey' && ((r === 'water' && snap.realmBlend < 0.5) || (r === 'coral' && snap.realmBlend >= 0.5)));
          btn.classList.toggle('is-active', active);
          btn.setAttribute('aria-pressed', snap.mode === r ? 'true' : 'false');
        }
        if (fallbackImg) {
          fallbackImg.src = snap.realmBlend >= 0.5
            ? './assets/img/kioku-dragon-round35-coral-fallback.webp'
            : './assets/img/kioku-dragon-round35-water-fallback.webp';
        }
      };

      const onToggleClick = () => syncUi(realmState.setPaused(!realmState.isPaused()));
      const onResetClick = () => orbit.reset();
      const realmHandlers = realmBtns.map((btn) => {
        const fn = () => {
          const r = btn.dataset.realmSelect;
          syncUi(realmState.setMode(realmState.getMode() === r ? 'journey' : r));
        };
        btn.addEventListener('click', fn);
        return [btn, fn];
      });
      toggleBtn?.addEventListener('click', onToggleClick);
      resetBtn?.addEventListener('click', onResetClick);

      let inViewport = true;
      const io = typeof IntersectionObserver === 'function'
        ? new IntersectionObserver((entries) => { if (entries[0]) inViewport = entries[0].isIntersecting; }, { threshold: 0.04 })
        : null;
      io?.observe(stage);

      let meshCount = 0, vertCount = 0, boneCount = 0;
      dragonRoot.traverse((o) => {
        if (o.isMesh && o.geometry?.attributes?.position) {
          meshCount++;
          vertCount += o.geometry.attributes.position.count;
        }
        if (o.isSkinnedMesh && o.skeleton) boneCount = Math.max(boneCount, o.skeleton.bones.length);
      });

      let rafId = 0, lastTs = performance.now(), elapsed = 0, fpsSmooth = 60, stopped = false;

      const tick = (now) => {
        if (stopped) return;
        if (motionQuery.matches) {
          cleanup();
          activateStaticFallback('reduced-motion');
          return;
        }
        rafId = requestAnimationFrame(tick);
        if (!inViewport || document.hidden) {
          lastTs = now;
          return;
        }
        const dt = Math.min(0.08, Math.max(0.001, (now - lastTs) / 1000));
        lastTs = now;
        fpsSmooth = fpsSmooth * 0.92 + (1 / dt) * 0.08;

        const snap = realmState.step(dt);
        switchClip(snap.activeClip);
        if (!snap.paused) {
          elapsed += dt;
          mixer.update(dt);
        }

        dragonPivot.position.y = snap.elevation * 0.42;
        dragonPivot.rotation.z = snap.pitch;
        orbit.step(dt, camera, 0.92, 0.10 + dragonPivot.position.y * 0.45, 0);

        matBridge.update(snap, elapsed);
        env.update(snap, elapsed);
        renderer.render(scene, camera);
        syncUi(snap);

        window.__KIOKU_DRAGON_DIAG__ = {
          mode: 'webgl-round35',
          asset: './assets/models/KIOKU-Dragon-Web.glb',
          meshCount,
          vertCount,
          boneCount,
          clips: Object.keys(actions),
          activeClip: currentClipName,
          realmMode: snap.mode,
          phaseName: snap.phaseName,
          realmBlend: Number(snap.realmBlend.toFixed(4)),
          paused: snap.paused,
          fps: Number(fpsSmooth.toFixed(1)),
          drawCalls: renderer.info.render.calls,
          triangles: renderer.info.render.triangles,
          orbitYaw: Number(orbit.current.yaw.toFixed(3)),
          orbitPitch: Number(orbit.current.pitch.toFixed(3)),
        };
      };

      const onContextLost = (e) => {
        e.preventDefault();
        cleanup();
        activateStaticFallback('webgl-context-lost');
      };
      canvas.addEventListener('webglcontextlost', onContextLost);

      function cleanup() {
        if (stopped) return;
        stopped = true;
        cancelAnimationFrame(rafId);
        io?.disconnect();
        window.removeEventListener?.('resize', resize);
        canvas.removeEventListener('webglcontextlost', onContextLost);
        toggleBtn?.removeEventListener('click', onToggleClick);
        resetBtn?.removeEventListener('click', onResetClick);
        for (const [b, fn] of realmHandlers) b.removeEventListener('click', fn);
        orbit.dispose();
        env.dispose();
        matBridge.dispose();
        renderer.dispose();
        activeCleanup = null;
      }

      activeCleanup = cleanup;
      setExtraControlsHidden(false);
      sceneRoot.classList.add('is-ready');
      syncUi(realmState.step(0.016));
      mixer.update(0.016);
      orbit.step(0.016, camera, 0.92, 0.10, 0);
      renderer.render(scene, camera);
      rafId = requestAnimationFrame(tick);
    } catch (err) {
      activateStaticFallback('init-error');
      window.__KIOKU_DRAGON_ERROR__ = String(err?.message || err);
    }
  }

  const onMotionPrefChange = () => {
    if (motionQuery.matches) {
      bootToken++;
      activeCleanup?.();
      activateStaticFallback('reduced-motion');
    } else if (!activeCleanup) {
      mountWebGLScene(++bootToken);
    }
  };
  if (typeof motionQuery.addEventListener === 'function') motionQuery.addEventListener('change', onMotionPrefChange);
  else if (typeof motionQuery.addListener === 'function') motionQuery.addListener(onMotionPrefChange);

  mountWebGLScene(++bootToken);
})();
