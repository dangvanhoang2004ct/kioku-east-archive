// KIOKU 3D Dragon Interactive Orbit & Framing Controller
// Supports pointer drag, keyboard arrow rotation, smooth damping, and Reset view.

export function createDragonOrbitController(canvas, stageRoot) {
  const defaults = { yaw: 0.14, pitch: 0.06, distance: 9.6 };
  const target = { ...defaults };
  const current = { ...defaults };
  let dragging = false;
  let origin = { x: 0, y: 0, yaw: 0, pitch: 0 };

  const clampPitch = (p) => Math.max(-0.42, Math.min(0.52, p));

  const onPointerDown = (e) => {
    if (e.button !== undefined && e.button !== 0) return;
    dragging = true;
    origin = { x: e.clientX, y: e.clientY, yaw: target.yaw, pitch: target.pitch };
    canvas.setPointerCapture?.(e.pointerId);
  };

  const onPointerMove = (e) => {
    if (!dragging) return;
    const dx = (e.clientX - origin.x) / Math.max(240, stageRoot.clientWidth || canvas.clientWidth || 320);
    const dy = (e.clientY - origin.y) / Math.max(200, stageRoot.clientHeight || canvas.clientHeight || 240);
    target.yaw = origin.yaw - dx * 2.2;
    target.pitch = clampPitch(origin.pitch + dy * 1.3);
  };

  const onPointerUp = () => {
    dragging = false;
  };

  const onKeyDown = (e) => {
    const step = 0.12;
    if (e.key === 'ArrowLeft') target.yaw += step;
    else if (e.key === 'ArrowRight') target.yaw -= step;
    else if (e.key === 'ArrowUp') target.pitch = clampPitch(target.pitch + step * 0.7);
    else if (e.key === 'ArrowDown') target.pitch = clampPitch(target.pitch - step * 0.7);
    else return;
    e.preventDefault();
  };

  canvas.addEventListener('pointerdown', onPointerDown);
  canvas.addEventListener('pointermove', onPointerMove);
  canvas.addEventListener('pointerup', onPointerUp);
  canvas.addEventListener('pointercancel', onPointerUp);
  canvas.addEventListener('keydown', onKeyDown);

  return {
    current,
    target,
    setViewportWidth(width, height = 600) {
      const aspect = Math.max(0.45, width / Math.max(1, height));
      const baseDist = 9.5;
      defaults.distance = aspect < 1.65 ? baseDist * (1.65 / Math.max(0.82, aspect)) : baseDist;
      target.distance = defaults.distance;
    },
    reset() {
      target.yaw = defaults.yaw;
      target.pitch = defaults.pitch;
      target.distance = defaults.distance;
    },
    step(dt, camera, lookAtX, lookAtY, lookAtZ) {
      const damp = 1 - Math.exp(-dt * 7.5);
      current.yaw += (target.yaw - current.yaw) * damp;
      current.pitch += (target.pitch - current.pitch) * damp;
      current.distance += (target.distance - current.distance) * damp;
      const cp = Math.cos(current.pitch);
      camera.position.set(
        lookAtX + Math.sin(current.yaw) * cp * current.distance,
        lookAtY + Math.sin(current.pitch) * current.distance,
        lookAtZ + Math.cos(current.yaw) * cp * current.distance
      );
      camera.lookAt(lookAtX, lookAtY + 0.05, lookAtZ);
    },
    dispose() {
      canvas.removeEventListener('pointerdown', onPointerDown);
      canvas.removeEventListener('pointermove', onPointerMove);
      canvas.removeEventListener('pointerup', onPointerUp);
      canvas.removeEventListener('pointercancel', onPointerUp);
      canvas.removeEventListener('keydown', onKeyDown);
    },
  };
}
