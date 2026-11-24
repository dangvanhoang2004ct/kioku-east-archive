// KIOKU Round-35 Dual-Realm State & Journey Controller
// Maps continuous realmBlend (0..1) and journey phases to Blender Stage-E/F controls.

const clamp01 = (v) => Math.max(0, Math.min(1, v));
const smoothstep = (e0, e1, x) => {
  const t = clamp01((x - e0) / Math.max(1e-5, e1 - e0));
  return t * t * (3 - 2 * t);
};
const lerp = (a, b, t) => a + (b - a) * t;

// Exact normalized spline from Round-35 E_TransitionAction.001 (frames 422..457)
const TRANSITION_KNOTS = [
  [0.0, 0.0, 1.0],
  [5 / 35, 0.16, 0.84],
  [11 / 35, 0.38, 0.60],
  [17 / 35, 0.64, 0.34],
  [25 / 35, 0.88, 0.14],
  [1.0, 1.0, 0.06],
];

export function sampleRound35TransitionCurve(u) {
  const t = clamp01(u);
  for (let i = 0; i < TRANSITION_KNOTS.length - 1; i++) {
    const a = TRANSITION_KNOTS[i];
    const b = TRANSITION_KNOTS[i + 1];
    if (t <= b[0] || i === TRANSITION_KNOTS.length - 2) {
      const local = smoothstep(a[0], b[0], t);
      return {
        state: lerp(a[1], b[1], local),
        wet: lerp(a[2], b[2], local),
      };
    }
  }
  return { state: 1, wet: 0.06 };
}

export const JOURNEY_CYCLE_SECONDS = 26.0;

function evaluateJourneyPhase(phase) {
  const p = ((phase % 1) + 1) % 1;

  // 1. Underwater swimming (0.00 -> 0.24)
  if (p < 0.24) {
    const u = p / 0.24;
    return {
      phaseName: 'underwater',
      stageLabel: 'Water Realm · Underwater Guardian',
      clip: 'SwimLoop',
      state: 0.0,
      wet: 1.0,
      submerged: 1.0,
      aura: 0.0,
      coralLight: 0.0,
      elevation: -0.55 + 0.12 * Math.sin(u * Math.PI * 2),
      pitch: 0.03 * Math.sin(u * Math.PI * 2),
      surfacePulse: 0.0,
    };
  }

  // 2. Ascent & Surface Crossing (0.24 -> 0.40)
  if (p < 0.40) {
    const u = (p - 0.24) / 0.16;
    const breach = smoothstep(0.15, 0.88, u);
    const pulse = Math.sin(clamp01((u - 0.22) / 0.68) * Math.PI);
    return {
      phaseName: u < 0.48 ? 'ascent' : 'surface',
      stageLabel: u < 0.48 ? 'Water Realm · Ascending' : 'Surface Crossing',
      clip: 'SurfaceCrossing',
      state: 0.0,
      wet: 1.0,
      submerged: 1.0 - smoothstep(0.32, 0.82, u),
      aura: 0.0,
      coralLight: 0.0,
      elevation: lerp(-0.52, 0.42, breach),
      pitch: lerp(0.16, 0.08, u) * Math.sin(u * Math.PI),
      surfacePulse: Math.max(0, pulse),
    };
  }

  // 3. Water -> Coral Transformation (0.40 -> 0.56)
  if (p < 0.56) {
    const u = (p - 0.40) / 0.16;
    const curve = sampleRound35TransitionCurve(u);
    const energy = smoothstep(0.18, 0.95, u);
    return {
      phaseName: 'transform',
      stageLabel: 'Realm Transformation · Water to Coral',
      clip: 'WaterToCoralTransform',
      state: curve.state,
      wet: curve.wet,
      submerged: 0.0,
      aura: energy,
      coralLight: energy,
      elevation: lerp(0.42, 0.86, smoothstep(0, 1, u)),
      pitch: 0.09 * Math.sin(u * Math.PI),
      surfacePulse: Math.max(0, (1 - u * 2.2) * 0.35),
    };
  }

  // 4. Coral Celestial Flight (0.56 -> 0.84)
  if (p < 0.84) {
    const u = (p - 0.56) / 0.28;
    return {
      phaseName: 'celestial',
      stageLabel: 'Coral Flight · Guardian of the Sky',
      clip: 'CoralFlightLoop',
      state: 1.0,
      wet: 0.06,
      submerged: 0.0,
      aura: 1.0,
      coralLight: 1.0,
      elevation: 0.86 + 0.14 * Math.sin(u * Math.PI * 2),
      pitch: 0.04 * Math.cos(u * Math.PI * 2),
      surfacePulse: 0.0,
    };
  }

  // 5. Descent & Return to Water (0.84 -> 1.00)
  const u = (p - 0.84) / 0.16;
  const revCurve = sampleRound35TransitionCurve(1.0 - smoothstep(0.0, 0.78, u));
  const plunge = smoothstep(0.45, 0.92, u);
  const pulse = Math.sin(clamp01((u - 0.42) / 0.52) * Math.PI);
  return {
    phaseName: 'descent',
    stageLabel: 'Returning to the Water Realm',
    clip: u < 0.82 ? 'CoralToWaterDescent' : 'SwimLoop',
    state: revCurve.state,
    wet: Math.max(revCurve.wet, plunge),
    submerged: plunge,
    aura: clamp01(1.0 - smoothstep(0.0, 0.65, u)),
    coralLight: clamp01(1.0 - smoothstep(0.0, 0.70, u)),
    elevation: lerp(0.86, -0.55, smoothstep(0.05, 0.96, u)),
    pitch: -0.16 * Math.sin(u * Math.PI),
    surfacePulse: Math.max(0, pulse * 0.85),
  };
}

export function createDragonRealmState(options = {}) {
  let mode = options.initialMode || 'journey'; // 'journey' | 'water' | 'coral'
  let explicitPaused = Boolean(options.paused);
  let journeyTime = Number(options.initialTime || 0);

  const snapshot = {
    mode,
    paused: explicitPaused,
    phaseName: 'underwater',
    stageLabel: 'Water Realm · Underwater Guardian',
    activeClip: 'SwimLoop',
    realmBlend: 0.0,
    kioku_state: 0.0,
    kioku_wet: 1.0,
    kioku_submerged: 1.0,
    kioku_fx_emission: 1.0,
    kioku_fx_aura: 0.0,
    kioku_fx_coral_light: 0.0,
    kioku_fx_atmo: 1.0,
    elevation: -0.55,
    pitch: 0.0,
    surfacePulse: 0.0,
  };

  function step(dtSeconds) {
    const dt = Math.max(0, Math.min(0.1, Number(dtSeconds) || 0));
    if (!explicitPaused && mode === 'journey') {
      journeyTime = (journeyTime + dt) % JOURNEY_CYCLE_SECONDS;
    }

    let target;
    if (mode === 'water') {
      target = {
        phaseName: 'underwater',
        stageLabel: 'Water Realm · Guardian of Memories',
        clip: 'SwimLoop',
        state: 0.0,
        wet: 1.0,
        submerged: 1.0,
        aura: 0.0,
        coralLight: 0.0,
        elevation: -0.45,
        pitch: 0.0,
        surfacePulse: 0.0,
      };
    } else if (mode === 'coral') {
      target = {
        phaseName: 'celestial',
        stageLabel: 'Coral Flight · Guardian of the Sky',
        clip: 'CoralFlightLoop',
        state: 1.0,
        wet: 0.06,
        submerged: 0.0,
        aura: 1.0,
        coralLight: 1.0,
        elevation: 0.82,
        pitch: 0.02,
        surfacePulse: 0.0,
      };
    } else {
      target = evaluateJourneyPhase(journeyTime / JOURNEY_CYCLE_SECONDS);
    }

    // Smoothly damp toward target even when paused so manual realm clicks transition smoothly
    const rate = mode === 'journey' ? 1 - Math.exp(-dt * 9.0) : 1 - Math.exp(-Math.max(dt, 0.016) * 3.2);
    snapshot.mode = mode;
    snapshot.paused = explicitPaused;
    snapshot.phaseName = target.phaseName;
    snapshot.stageLabel = target.stageLabel;
    snapshot.activeClip = target.clip;
    snapshot.kioku_state = lerp(snapshot.kioku_state, target.state, rate);
    snapshot.realmBlend = snapshot.kioku_state;
    snapshot.kioku_wet = lerp(snapshot.kioku_wet, target.wet, rate);
    snapshot.kioku_submerged = lerp(snapshot.kioku_submerged, target.submerged, rate);
    snapshot.kioku_fx_aura = lerp(snapshot.kioku_fx_aura, target.aura, rate);
    snapshot.kioku_fx_coral_light = lerp(snapshot.kioku_fx_coral_light, target.coralLight, rate);
    snapshot.elevation = lerp(snapshot.elevation, target.elevation, rate);
    snapshot.pitch = lerp(snapshot.pitch, target.pitch, rate);
    snapshot.surfacePulse = lerp(snapshot.surfacePulse, target.surfacePulse, rate);
    return snapshot;
  }

  return {
    step,
    getSnapshot: () => snapshot,
    setMode(nextMode) {
      if (nextMode === 'water' || nextMode === 'coral' || nextMode === 'journey') {
        mode = nextMode;
        snapshot.mode = mode;
      }
      return snapshot;
    },
    setPaused(nextPaused) {
      explicitPaused = Boolean(nextPaused);
      snapshot.paused = explicitPaused;
      return snapshot;
    },
    isPaused: () => explicitPaused,
    getMode: () => mode,
  };
}
