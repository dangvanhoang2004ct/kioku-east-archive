#!/usr/bin/env python3
"""KIOKU River Guardian — Production 3D Sculpt & Rig Builder in Blender 5.3 (Pass 2).

Faithfully reproduces the approved 2D KIOKU brand identity artwork in 3D:
1. True KIOKU S-curve spine: sweeping rear arch (+1.12), deep mid-body trough (-0.64),
   steep rising neck arch (+0.72), and poised aristocratic head (+0.68..+0.78).
2. Sleek, smooth dorsal spine (no shark-fin spikes or warty flank bumps) with the
   signature flowing dorsal neck fin and curved ventral neck ribbon from the artwork.
3. Unified, cohesive East Asian river dragon head (no jaw gap):
   - Wedge cranium, concave nasal bridge, slightly upturned snout with nostril rim.
   - Flush muted-teal snout bridge & angular cheek highlight plate.
   - Flush pale ice-blue lower jaw border & 3 sleek rear chin beard tufts.
   - Upturned almond eye (lower at back-cheek, sweeping up toward snout bridge)
     with dark navy iris/pupil and overarching pale-mist/navy eyebrow ridge.
4. Integrated stag antlers (sturdy deep-navy Y-forked front antler + swept muted-teal
   rear antler), cohesive S-curved flame mane locks hugging the head/neck, and a
   single pair of calligraphy S-curved whiskers.
5. Sculpted dragon forelimbs at the lower trough with 3 curved claws, and a sleek
   tapering whip tail ending in the two-pronged flame tail fin.
"""
from __future__ import annotations
import json, math, struct
from pathlib import Path
import numpy as np
import bpy

ROOT = Path(__file__).resolve().parents[1]
SRC_GLB = ROOT / 'assets' / 'models' / 'kioku-river-guardian-v2.glb'
OUT_GLB = ROOT / 'assets' / 'models' / 'kioku-river-guardian-v6-longform.glb'
OUT_BLEND = ROOT / 'assets' / 'models' / 'kioku-river-guardian-production.blend'

PI = math.pi
TAU = 2.0 * PI


def load_glb(path: Path):
    blob = path.read_bytes()
    magic, ver, length = struct.unpack_from('<4sII', blob, 0)
    assert (magic, ver, length) == (b'glTF', 2, len(blob))
    jlen, jtype = struct.unpack_from('<I4s', blob, 12)
    assert jtype == b'JSON'
    gltf = json.loads(blob[20:20 + jlen])
    off = 20 + jlen
    blen, btype = struct.unpack_from('<I4s', blob, off)
    assert btype == b'BIN\0'
    return gltf, bytearray(blob[off + 8:off + 8 + blen])


gltf, raw = load_glb(SRC_GLB)
D = {5121: np.dtype('u1'), 5123: np.dtype('<u2'), 5125: np.dtype('<u4'), 5126: np.dtype('<f4')}
N = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def get_acc(idx: int) -> np.ndarray:
    a = gltf['accessors'][idx]
    v = gltf['bufferViews'][a['bufferView']]
    n = N[a['type']]
    off = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(raw, dtype=D[a['componentType']], count=a['count'] * n, offset=off).reshape(-1, n).copy()


# ---------------------------------------------------------------------------
# 1. True KIOKU S-Curve Spine & 10-Bone Skeleton
# ---------------------------------------------------------------------------
SPINE_X = np.array([
    -5.15, -4.55, -3.85, -3.10, -2.30, -1.50, -0.70, +0.08,
    +0.55, +0.98, +1.42, +1.82, +2.12
], dtype=float)
SPINE_Y = np.array([
    -0.42, -0.18, +0.36, +0.92, +1.14, +0.78, +0.02, -0.58,
    -0.42, +0.32, +0.82, +0.74, +0.64
], dtype=float)
SPINE_Z = np.array([
    +0.02, +0.04, +0.03, +0.00, -0.04, -0.04, -0.01, +0.03,
    +0.04, +0.02, +0.00, -0.01, +0.00
], dtype=float)
SPINE_RY = np.array([
    0.032, 0.068, 0.130, 0.195, 0.242, 0.258, 0.265, 0.270,
    0.262, 0.248, 0.238, 0.248, 0.255
], dtype=float)
SPINE_RZ = np.array([
    0.030, 0.064, 0.122, 0.182, 0.228, 0.242, 0.248, 0.252,
    0.245, 0.232, 0.225, 0.240, 0.255
], dtype=float)


def catmull_rom_1d(xp: np.ndarray, yp: np.ndarray, x_eval: float) -> float:
    x_eval = float(np.clip(x_eval, xp[0], xp[-1]))
    i = int(np.searchsorted(xp, x_eval, side='right')) - 1
    i = max(0, min(len(xp) - 2, i))
    t = (x_eval - xp[i]) / max(1e-8, xp[i + 1] - xp[i])
    p0 = yp[max(0, i - 1)]
    p1 = yp[i]
    p2 = yp[i + 1]
    p3 = yp[min(len(yp) - 1, i + 2)]
    return float(0.5 * (
        (2.0 * p1)
        + (-p0 + p2) * t
        + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * (t * t)
        + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * (t * t * t)
    ))


def spine_at(x: float):
    y = catmull_rom_1d(SPINE_X, SPINE_Y, x)
    z = catmull_rom_1d(SPINE_X, SPINE_Z, x)
    ry = catmull_rom_1d(SPINE_X, SPINE_RY, x)
    rz = catmull_rom_1d(SPINE_X, SPINE_RZ, x)
    return np.array([x, y, z], dtype=np.float64), ry, rz


def spine_frame(x: float):
    dx = 0.02
    p_minus, _, _ = spine_at(max(SPINE_X[0], x - dx))
    p_plus, _, _ = spine_at(min(SPINE_X[-1], x + dx))
    tan = p_plus - p_minus
    tan /= max(1e-8, np.linalg.norm(tan))
    world_z = np.array([0.0, 0.0, 1.0])
    up = np.cross(world_z, tan)
    if np.linalg.norm(up) < 1e-5:
        up = np.array([0.0, 1.0, 0.0])
    else:
        up /= np.linalg.norm(up)
    side = np.cross(tan, up)
    side /= max(1e-8, np.linalg.norm(side))
    return tan, up, side


BONE_WORLD_X = np.array([
    2.02, 1.40, 0.72, 0.02, -0.78, -1.58, -2.38, -3.18, -3.98, -4.75
], dtype=float)
BONE_WORLD_POS = np.array([spine_at(bx)[0] for bx in BONE_WORLD_X], dtype=np.float64)

joints = gltf['skins'][0]['joints']
assert len(joints) == 10
inv_bind_mats = []
for idx, nid in enumerate(joints):
    node = gltf['nodes'][nid]
    if idx == 0:
        node['translation'] = [round(float(v), 5) for v in BONE_WORLD_POS[0]]
    else:
        rel = BONE_WORLD_POS[idx] - BONE_WORLD_POS[idx - 1]
        node['translation'] = [round(float(v), 5) for v in rel]
    node['rotation'] = [0.0, 0.0, 0.0, 1.0]
    wx, wy, wz = BONE_WORLD_POS[idx]
    inv_bind_mats.append([
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        -float(wx), -float(wy), -float(wz), 1.0
    ])
inv_bind_arr = np.array(inv_bind_mats, dtype='<f4')


def skin_weights(x: float, prefer_head: bool = False, fixed_joint: int | None = None):
    if fixed_joint is not None:
        return np.array([fixed_joint, 0, 0, 0], dtype=np.uint16), np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    if prefer_head or x >= BONE_WORLD_X[0]:
        return np.array([0, 0, 0, 0], dtype=np.uint16), np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    if x <= BONE_WORLD_X[-1]:
        return np.array([9, 0, 0, 0], dtype=np.uint16), np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    for i in range(9):
        if BONE_WORLD_X[i] >= x >= BONE_WORLD_X[i + 1]:
            u = (BONE_WORLD_X[i] - x) / max(1e-8, BONE_WORLD_X[i] - BONE_WORLD_X[i + 1])
            s = u * u * (3.0 - 2.0 * u)
            return (
                np.array([i, i + 1, 0, 0], dtype=np.uint16),
                np.array([1.0 - s, s, 0.0, 0.0], dtype=np.float32),
            )
    return np.array([9, 0, 0, 0], dtype=np.uint16), np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)


# ---------------------------------------------------------------------------
# 2. Geometry Builders
# ---------------------------------------------------------------------------
prims_data = {i: {'V': [], 'F': [], 'J': [], 'W': [], 'offset': 0} for i in range(6)}


def add_mesh(mat_idx: int, V: np.ndarray, F: np.ndarray, J: np.ndarray, W: np.ndarray):
    if len(V) == 0 or len(F) == 0:
        return
    bucket = prims_data[mat_idx]
    off = bucket['offset']
    bucket['V'].append(np.asarray(V, dtype=np.float32))
    bucket['F'].append(np.asarray(F, dtype=np.int32) + off)
    bucket['J'].append(np.asarray(J, dtype=np.uint16))
    bucket['W'].append(np.asarray(W, dtype=np.float32))
    bucket['offset'] += len(V)


def catmull_curve(anchors, res: int = 8) -> np.ndarray:
    p = np.asarray(anchors, dtype=np.float64)
    out = []
    for i in range(len(p) - 1):
        p0 = p[max(0, i - 1)]
        p1 = p[i]
        p2 = p[i + 1]
        p3 = p[min(len(p) - 1, i + 2)]
        for j in range(res):
            t = j / float(res)
            pt = 0.5 * (
                (2.0 * p1)
                + (-p0 + p2) * t
                + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * (t * t)
                + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * (t * t * t)
            )
            out.append(pt)
    out.append(p[-1])
    return np.array(out, dtype=np.float64)


def build_sculpted_tube(
    anchors, r_start: float, r_end: float, sides: int = 10, res: int = 7,
    prefer_head: bool = False, fixed_joint: int | None = None,
    aspect_y: float = 1.0, bulge: float = 0.12, cap_ends: bool = True
):
    pts = catmull_curve(anchors, res=res)
    n = len(pts)
    V, F, J, W = [], [], [], []
    for i, p in enumerate(pts):
        u = i / max(1, n - 1)
        env = (1.0 - u) * r_start + u * r_end + bulge * r_start * math.sin(PI * u)
        if u > 0.88:
            # Smooth rounded tip instead of needle spike
            t_tip = (u - 0.88) / 0.12
            env *= math.cos(0.45 * PI * t_tip)
        tan = pts[min(n - 1, i + 1)] - pts[max(0, i - 1)]
        tan /= max(1e-8, np.linalg.norm(tan))
        ref = np.array([0.0, 1.0, 0.0]) if abs(tan[1]) < 0.88 else np.array([0.0, 0.0, 1.0])
        side = np.cross(tan, ref)
        side /= max(1e-8, np.linalg.norm(side))
        up = np.cross(side, tan)
        up /= max(1e-8, np.linalg.norm(up))
        j, w = skin_weights(float(p[0]), prefer_head=prefer_head, fixed_joint=fixed_joint)
        for q in range(sides):
            ang = TAU * q / sides
            offset = up * (math.cos(ang) * env * aspect_y) + side * (math.sin(ang) * env)
            V.append(p + offset)
            J.append(j)
            W.append(w)
        if i > 0:
            for q in range(sides):
                a = (i - 1) * sides + q
                b = (i - 1) * sides + (q + 1) % sides
                c = i * sides + q
                d = i * sides + (q + 1) % sides
                F.append((a, c, b))
                F.append((b, c, d))
    if cap_ends and n >= 2:
        for end_i, flip in [(0, True), (n - 1, False)]:
            c_idx = len(V)
            p = pts[end_i]
            j, w = skin_weights(float(p[0]), prefer_head=prefer_head, fixed_joint=fixed_joint)
            V.append(p)
            J.append(j)
            W.append(w)
            ring0 = end_i * sides
            for q in range(sides):
                a = ring0 + q
                b = ring0 + (q + 1) % sides
                F.append((c_idx, b, a) if flip else (c_idx, a, b))
    return np.array(V, np.float32), np.array(F, np.int32), np.array(J, np.uint16), np.array(W, np.float32)


def build_3d_plume(
    anchors, max_width: float, max_thick: float, width_dir=(0.0, 1.0, 0.0),
    res: int = 7, prefer_head: bool = False, fixed_joint: int | None = None,
    root_scale: float = 0.45
):
    pts = catmull_curve(anchors, res=res)
    n = len(pts)
    w_axis = np.asarray(width_dir, dtype=np.float64)
    w_axis /= max(1e-8, np.linalg.norm(w_axis))
    V, F, J, W = [], [], [], []
    sides = 6
    for i, p in enumerate(pts):
        u = i / max(1, n - 1)
        # Broad cohesive root that swells slightly then tapers cleanly to a curved flame tip
        profile = (root_scale * (1.0 - u) + math.sin(PI * u) * 0.92) * (1.0 - 0.18 * u * u)
        if u > 0.82:
            profile *= max(0.03, (1.0 - u) / 0.18)
        w_rad = max_width * profile
        t_rad = max_thick * profile
        tan = pts[min(n - 1, i + 1)] - pts[max(0, i - 1)]
        tan /= max(1e-8, np.linalg.norm(tan))
        across = w_axis - np.dot(w_axis, tan) * tan
        if np.linalg.norm(across) < 1e-5:
            across = np.array([0.0, 1.0, 0.0])
        across /= max(1e-8, np.linalg.norm(across))
        normal = np.cross(tan, across)
        normal /= max(1e-8, np.linalg.norm(normal))
        j, w = skin_weights(float(p[0]), prefer_head=prefer_head, fixed_joint=fixed_joint)
        ring_pts = [
            p + across * w_rad,
            p + across * (0.35 * w_rad) + normal * t_rad,
            p - across * (0.35 * w_rad) + normal * (0.85 * t_rad),
            p - across * w_rad,
            p - across * (0.35 * w_rad) - normal * (0.85 * t_rad),
            p + across * (0.35 * w_rad) - normal * t_rad,
        ]
        for rp in ring_pts:
            V.append(rp)
            J.append(j)
            W.append(w)
        if i > 0:
            for q in range(sides):
                a = (i - 1) * sides + q
                b = (i - 1) * sides + (q + 1) % sides
                c = i * sides + q
                d = i * sides + (q + 1) % sides
                F.append((a, c, b))
                F.append((b, c, d))
    tip_idx = len(V)
    p_tip = pts[-1]
    j, w = skin_weights(float(p_tip[0]), prefer_head=prefer_head, fixed_joint=fixed_joint)
    V.append(p_tip)
    J.append(j)
    W.append(w)
    ring_last = (n - 1) * sides
    for q in range(sides):
        F.append((ring_last + q, tip_idx, ring_last + (q + 1) % sides))
    return np.array(V, np.float32), np.array(F, np.int32), np.array(J, np.uint16), np.array(W, np.float32)


# ---------------------------------------------------------------------------
# 3. Sculpt the Sleek Serpentine Body (Smooth Dorsal Navy, River-Blue Flanks, Segmented Belly)
# ---------------------------------------------------------------------------
RINGS = 180
xs = np.linspace(SPINE_X[0], SPINE_X[-1], RINGS)


def build_strip(angles: np.ndarray, mat_idx: int, radial_mod_fn=None):
    V, F, J, W = [], [], [], []
    cols = len(angles)
    for i, x in enumerate(xs):
        center, ry, rz = spine_at(float(x))
        tan, up, side = spine_frame(float(x))
        j, w = skin_weights(float(x))
        for k, ang in enumerate(angles):
            rmod = radial_mod_fn(float(x), float(ang), i, k) if radial_mod_fn else 1.0
            local_up = math.cos(ang) * ry * rmod
            local_side = math.sin(ang) * rz * rmod
            pt = center + up * local_up + side * local_side
            V.append(pt)
            J.append(j)
            W.append(w)
        if i > 0:
            for k in range(cols - 1):
                a = (i - 1) * cols + k
                b = a + 1
                c = i * cols + k
                d = c + 1
                F.append((a, c, b))
                F.append((b, c, d))
    add_mesh(mat_idx, V, F, J, W)


# Smooth deep-navy dorsal spine (Mat 1) — sleek continuous ridge, NO spiky shark fins!
dorsal_angles = np.linspace(-0.62, 0.62, 11)
def dorsal_mod(x, ang, i, k):
    return 1.0 + 0.08 * math.exp(-((ang / 0.28) ** 2))
build_strip(dorsal_angles, 1, dorsal_mod)

# Smooth river-blue flanks (Mat 0) + flush muted-teal upper-flank band (Mat 3)
teal_r_angles = np.linspace(0.58, 0.92, 5)
teal_l_angles = np.linspace(-0.92, -0.58, 5)
build_strip(teal_r_angles, 3)
build_strip(teal_l_angles, 3)

flank_r_angles = np.linspace(0.88, 2.28, 12)
flank_l_angles = np.linspace(-2.28, -0.88, 12)
build_strip(flank_r_angles, 0)
build_strip(flank_l_angles, 0)

# Segmented pale ice-blue underbelly (Mat 2) with flush transverse scutes
belly_angles = np.linspace(2.22, 2.0 * PI - 2.22, 11)
def belly_mod(x, ang, i, k):
    seg_phase = math.cos((x + 5.0) * (TAU / 0.36))
    groove = -0.025 * max(0.0, seg_phase) ** 3
    belly_flat = 0.96 + 0.04 * math.cos((ang - PI) * 1.5)
    return belly_flat + groove
build_strip(belly_angles, 2, belly_mod)

# Flush navy segment lines across the pale belly (Mat 1)
for x_seg in np.arange(-4.50, 1.90, 0.36):
    center, ry, rz = spine_at(float(x_seg))
    tan, up, side = spine_frame(float(x_seg))
    seg_pts = [
        center + up * (math.cos(ang) * ry * 0.975) + side * (math.sin(ang) * rz * 0.975)
        for ang in np.linspace(2.32, 2.0 * PI - 2.32, 9)
    ]
    add_mesh(1, *build_sculpted_tube(seg_pts, 0.009, 0.009, sides=6, res=2, bulge=0.0, cap_ends=False))

# Signature KIOKU Dorsal Neck Fin & Ventral Neck Ribbon (from the middle close-up in brand sheet)
# 1. Flowing deep-navy dorsal fin on the rising neck arch (x = 0.75 .. 1.25)
neck_d_p, neck_d_ry, _ = spine_at(1.08)
add_mesh(1, *build_3d_plume([
    neck_d_p + np.array([+0.20, neck_d_ry * 0.65, 0.0]),
    neck_d_p + np.array([-0.06, neck_d_ry + 0.08, 0.0]),
    neck_d_p + np.array([-0.34, neck_d_ry + 0.02, 0.0]),
    neck_d_p + np.array([-0.56, neck_d_ry - 0.14, 0.0]),
], max_width=0.082, max_thick=0.034, width_dir=(0, 1, 0), res=7, root_scale=0.60))

# 2. Compact S-scroll ventral ribbon hugging the inside of the neck arch
ribbon_anchors = [
    spine_at(1.22)[0] + np.array([0.0, -0.24, 0.0]),
    spine_at(1.02)[0] + np.array([+0.12, -0.30, 0.0]),
    spine_at(0.84)[0] + np.array([+0.18, -0.22, 0.0]),
    spine_at(0.70)[0] + np.array([+0.10, -0.26, 0.0]),
]
add_mesh(0, *build_3d_plume(ribbon_anchors, max_width=0.056, max_thick=0.024, width_dir=(1, 0, 0), res=6, root_scale=0.45))


# ---------------------------------------------------------------------------
# 4. Sculpt the Unified East Asian River Dragon Head (Matching Brand Close-Up)
# ---------------------------------------------------------------------------
# Compact, aristocratic head tilted UPWARD (~22 degrees) from nape (x=1.88) to upturned nose (x=3.26)
HEAD_X = np.array([1.88, 2.12, 2.36, 2.60, 2.82, 3.02, 3.16, 3.26], dtype=float)
HEAD_Y_TOP = np.array([0.88, 0.96, 1.02, 0.96, 0.92, 0.94, 0.96, 0.90], dtype=float)
HEAD_Y_BOT = np.array([0.38, 0.34, 0.34, 0.41, 0.52, 0.64, 0.73, 0.78], dtype=float)
HEAD_RZ = np.array([0.26, 0.32, 0.34, 0.29, 0.22, 0.17, 0.14, 0.08], dtype=float)


def build_unified_head():
    j_head, w_head = skin_weights(2.5, prefer_head=True)
    nx = 32
    x_samples = np.linspace(HEAD_X[0], HEAD_X[-1], nx)

    def head_ring_point(x: float, ang: float, scale_r: float = 1.0):
        y_top = catmull_rom_1d(HEAD_X, HEAD_Y_TOP, x)
        y_bot = catmull_rom_1d(HEAD_X, HEAD_Y_BOT, x)
        rz = catmull_rom_1d(HEAD_X, HEAD_RZ, x) * scale_r
        cy = 0.5 * (y_top + y_bot)
        ry = 0.5 * (y_top - y_bot) * scale_r
        ca, sa = math.cos(ang), math.sin(ang)
        # Orbital depression around x in [2.48, 2.86], |ang| in [0.65, 1.35]
        eye_dep = 1.0 - 0.16 * math.exp(-(((x - 2.66) / 0.16) ** 2)) * math.exp(-(((abs(ang) - 1.00) / 0.28) ** 2))
        # Cheekbone sculpt flare around x in [2.32, 2.82], |ang| in [1.45, 2.10]
        cheek_fl = 1.0 + 0.12 * math.exp(-(((x - 2.56) / 0.22) ** 2)) * math.exp(-(((abs(ang) - 1.75) / 0.28) ** 2))
        y = cy + ca * ry * eye_dep
        z = sa * rz * eye_dep * cheek_fl
        return [x, y, z]

    # A. Main River-Blue Cranium, Snout & Upper Cheek Shell (Mat 0)
    V, F, J, W = [], [], [], []
    angles_main = np.linspace(-2.45, 2.45, 25)
    na = len(angles_main)
    for i, x in enumerate(x_samples):
        for ang in angles_main:
            V.append(head_ring_point(float(x), float(ang), 1.0))
            J.append(j_head)
            W.append(w_head)
        if i > 0:
            for k in range(na - 1):
                a = (i - 1) * na + k
                c = i * na + k
                F.append((a, c, a + 1))
                F.append((a + 1, c, c + 1))
    # Cap snout tip smoothly
    tip_idx = len(V)
    V.append([HEAD_X[-1] + 0.02, 0.84, 0.0])
    J.append(j_head)
    W.append(w_head)
    last_r = (nx - 1) * na
    for k in range(na - 1):
        F.append((last_r + k, tip_idx, last_r + k + 1))
    add_mesh(0, V, F, J, W)

    # B. Flush Pale Ice-Blue Ventral Jaw & Chin Rim (Mat 2) — closes the bottom of the head seamlessly!
    V_j, F_j, J_j, W_j = [], [], [], []
    angles_jaw = np.linspace(2.35, 2.0 * PI - 2.35, 11)
    nj = len(angles_jaw)
    jaw_xs = np.linspace(1.90, 2.98, 20)
    for i, x in enumerate(jaw_xs):
        for ang in angles_jaw:
            V_j.append(head_ring_point(float(x), float(ang), 1.015))
            J_j.append(j_head)
            W_j.append(w_head)
        if i > 0:
            for k in range(nj - 1):
                a = (i - 1) * nj + k
                c = i * nj + k
                F_j.append((a, c, a + 1))
                F_j.append((a + 1, c, c + 1))
    add_mesh(2, V_j, F_j, J_j, W_j)

    # C. Tapered Muted-Teal Dorsal Snout Bridge (Mat 3) — tapers to a point at brow & nose tip
    V_b, F_b, J_b, W_b = [], [], [], []
    angles_br = np.linspace(-1.0, 1.0, 7)
    nb = len(angles_br)
    br_xs = np.linspace(2.52, 3.23, 16)
    for i, x in enumerate(br_xs):
        u_b = i / max(1, len(br_xs) - 1)
        span = 0.52 * math.sin(PI * u_b) ** 0.65
        for ang in angles_br:
            V_b.append(head_ring_point(float(x), float(ang * span), 1.018))
            J_b.append(j_head)
            W_b.append(w_head)
        if i > 0:
            for k in range(nb - 1):
                a = (i - 1) * nb + k
                c = i * nb + k
                F_b.append((a, c, a + 1))
                F_b.append((a + 1, c, c + 1))
    add_mesh(3, V_b, F_b, J_b, W_b)

    # D. Tapered Crescent Muted-Teal Cheek/Jaw Highlight (Mat 3) on both sides
    for s in (-1.0, 1.0):
        cheek_pts = [
            head_ring_point(2.34, s * 2.12, 1.012),
            head_ring_point(2.52, s * 1.98, 1.020),
            head_ring_point(2.74, s * 1.86, 1.020),
            head_ring_point(2.96, s * 1.78, 1.015),
            head_ring_point(3.12, s * 1.74, 1.010),
        ]
        add_mesh(3, *build_3d_plume(
            cheek_pts, max_width=0.076, max_thick=0.024,
            width_dir=(0, 1, 0), res=6, prefer_head=True, root_scale=0.15
        ))

        # Deep-navy mouth line & upturned nostril crescent (Mat 1)
        mouth_pts = [head_ring_point(x, s * 1.88, 1.028) for x in np.linspace(2.52, 3.18, 8)]
        add_mesh(1, *build_sculpted_tube(mouth_pts, 0.013, 0.006, sides=6, res=3, prefer_head=True, bulge=0.0))

        nostril_rim = [
            head_ring_point(3.10, s * 0.58, 1.032),
            head_ring_point(3.17, s * 0.50, 1.038),
            head_ring_point(3.21, s * 0.68, 1.032),
        ]
        add_mesh(1, *build_sculpted_tube(nostril_rim, 0.012, 0.007, sides=6, res=3, prefer_head=True, bulge=0.0))

    # E. 3 Sleek Deep-Navy Chin Beard Tufts rooted directly into the rear lower jaw (Mat 1)
    for tx, ty, l_b in [(2.48, 0.36, 0.10), (2.32, 0.34, 0.12), (2.16, 0.36, 0.10)]:
        add_mesh(1, *build_3d_plume([
            (tx + 0.06, ty + 0.03, 0.0),
            (tx - 0.04, ty - l_b * 0.65, 0.0),
            (tx - 0.13, ty - l_b, 0.0),
        ], max_width=0.044, max_thick=0.022, width_dir=(0, 0, 1), res=4, prefer_head=True, root_scale=0.65))

    # -----------------------------------------------------------------------
    # F. Expressive Bold Almond Eyes & Muted-Teal/Navy Brow Ridge
    # -----------------------------------------------------------------------
    for s in (-1.0, 1.0):
        sclera_pts = [
            (2.43, 0.605, s * 0.300),
            (2.55, 0.655, s * 0.298),
            (2.68, 0.700, s * 0.274),
            (2.80, 0.730, s * 0.238),
        ]
        add_mesh(5, *build_3d_plume(
            sclera_pts, max_width=0.072, max_thick=0.032,
            width_dir=(-0.34, 0.94, 0.0), res=7, prefer_head=True, root_scale=0.14
        ))

        # Focused Dark Navy Pupil/Iris (Mat 1) in anterior half of almond eye
        pupil_pts = [
            (2.63, 0.682, s * 0.292),
            (2.70, 0.704, s * 0.276),
            (2.77, 0.720, s * 0.254),
        ]
        add_mesh(1, *build_3d_plume(
            pupil_pts, max_width=0.048, max_thick=0.035,
            width_dir=(-0.34, 0.94, 0.0), res=5, prefer_head=True, root_scale=0.38
        ))

        # Crisp Deep-Navy Upper Eyelid Crease (Mat 1)
        add_mesh(1, *build_sculpted_tube([
            (2.39, 0.610, s * 0.302),
            (2.54, 0.705, s * 0.300),
            (2.69, 0.748, s * 0.272),
            (2.82, 0.740, s * 0.232),
        ], 0.016, 0.008, sides=7, res=5, prefer_head=True, bulge=0.10))

        # Arching Muted-Teal Eyebrow Ridge (Mat 3) sweeping gracefully over the eye (so white eye pops!)
        add_mesh(3, *build_3d_plume([
            (2.35, 0.635, s * 0.304),
            (2.52, 0.765, s * 0.302),
            (2.68, 0.802, s * 0.276),
            (2.84, 0.765, s * 0.228),
        ], max_width=0.044, max_thick=0.025, width_dir=(-0.20, 0.98, s * 0.1), res=6, prefer_head=True, root_scale=0.18))


build_unified_head()


# ---------------------------------------------------------------------------
# 5. Stag Antler Horns, Cohesive Flowing Mane & Calligraphy Whiskers
# ---------------------------------------------------------------------------
for s in (-1.0, 1.0):
    # A. Front/Inner Deep-Navy Stag Antler (Mat 1) — bold 2-prong wide Y-fork tilting back-up
    front_horn_rear_main = [
        (2.30, 0.92, s * 0.14),
        (2.16, 1.12, s * 0.18),
        (1.98, 1.32, s * 0.21),
        (1.82, 1.48, s * 0.23),
    ]
    add_mesh(1, *build_sculpted_tube(
        front_horn_rear_main, 0.056, 0.016, sides=9, res=6, prefer_head=True, bulge=0.08
    ))
    # Forward-upward curving prong of the Y-fork (creates the iconic chalice/stag fork!)
    front_horn_fwd_prong = [
        (2.18, 1.10, s * 0.18),
        (2.26, 1.28, s * 0.20),
        (2.38, 1.46, s * 0.22),
        (2.44, 1.58, s * 0.23),
    ]
    add_mesh(1, *build_sculpted_tube(
        front_horn_fwd_prong, 0.044, 0.014, sides=8, res=5, prefer_head=True, bulge=0.06
    ))

    # B. Rear/Outer Muted-Teal Branching Antler (Mat 3)
    rear_horn_trunk = [
        (2.12, 0.88, s * 0.19),
        (1.90, 1.04, s * 0.24),
        (1.66, 1.18, s * 0.28),
        (1.44, 1.24, s * 0.31),
    ]
    add_mesh(3, *build_sculpted_tube(
        rear_horn_trunk, 0.046, 0.014, sides=8, res=6, prefer_head=True, bulge=0.06
    ))
    add_mesh(3, *build_sculpted_tube([
        (1.84, 1.08, s * 0.25),
        (1.70, 1.24, s * 0.28),
        (1.56, 1.36, s * 0.30),
    ], 0.030, 0.012, sides=7, res=4, prefer_head=True, bulge=0.04))

    # C. Cohesive, S-Curved Flame Mane Locks rooted inside the skull (Mat 1 & Mat 3)
    mane_locks = [
        ([(2.32, 0.86, s * 0.16), (2.02, 0.94, s * 0.24), (1.72, 0.96, s * 0.28), (1.46, 1.06, s * 0.29)], 0.095, 0.045, 1),
        ([(2.36, 0.74, s * 0.20), (1.98, 0.80, s * 0.29), (1.58, 0.75, s * 0.34), (1.26, 0.81, s * 0.35)], 0.118, 0.052, 1),
        ([(2.36, 0.64, s * 0.23), (2.00, 0.63, s * 0.32), (1.66, 0.56, s * 0.36), (1.38, 0.58, s * 0.37)], 0.058, 0.034, 3),
        ([(2.34, 0.56, s * 0.22), (1.94, 0.52, s * 0.31), (1.54, 0.44, s * 0.35), (1.22, 0.47, s * 0.36)], 0.110, 0.048, 1),
        ([(2.30, 0.45, s * 0.19), (1.98, 0.37, s * 0.27), (1.66, 0.30, s * 0.31), (1.40, 0.33, s * 0.32)], 0.088, 0.040, 1),
    ]
    for anchors, mw, mt, m_id in mane_locks:
        add_mesh(m_id, *build_3d_plume(
            anchors, max_width=mw, max_thick=mt, width_dir=(0, 1, 0),
            res=6, prefer_head=True, root_scale=0.65
        ))

# D. Single Pair of Graceful S-Curved Whiskers (Mat 3: muted teal)
whisker_up = [
    (3.10, 0.82, +0.12),
    (3.32, 0.92, +0.18),
    (3.56, 1.12, +0.24),
    (3.74, 1.34, +0.26),
    (3.76, 1.50, +0.24),
    (3.62, 1.56, +0.20),
]
whisker_down = [
    (3.08, 0.76, -0.12),
    (3.32, 0.66, -0.18),
    (3.58, 0.62, -0.24),
    (3.84, 0.66, -0.26),
    (4.00, 0.56, -0.24),
    (3.86, 0.44, -0.20),
]
add_mesh(3, *build_sculpted_tube(whisker_up, 0.015, 0.003, sides=8, res=7, prefer_head=True, bulge=0.0))
add_mesh(3, *build_sculpted_tube(whisker_down, 0.015, 0.003, sides=8, res=7, prefer_head=True, bulge=0.0))


# ---------------------------------------------------------------------------
# 6. Sculpted Dragon Forelimbs at the Lower Trough & Two-Pronged Flame Tail Fin
# ---------------------------------------------------------------------------
# In the approved KIOKU artwork, the dragon has one pair of sculpted limbs at the
# lower S-curve trough (around x = +0.15, Bone 3) with 3 curved claws, while the
# rear body coils cleanly without bulky hind legs.
cp_limb, ry_limb, rz_limb = spine_at(0.16)
for s in (-1.0, 1.0):
    shoulder = cp_limb + np.array([0.0, -ry_limb * 0.55, s * rz_limb * 0.78])
    elbow = shoulder + np.array([-0.14, -0.26, s * 0.12])
    wrist = elbow + np.array([+0.12, -0.24, s * 0.04])
    palm = wrist + np.array([+0.11, -0.05, s * 0.02])
    add_mesh(0, *build_sculpted_tube(
        [shoulder, elbow, wrist, palm],
        0.090, 0.040, sides=10, res=6, fixed_joint=3, bulge=0.16
    ))
    add_mesh(1, *build_3d_plume([
        elbow + np.array([0.02, 0.03, s * 0.02]),
        elbow + np.array([-0.16, -0.02, s * 0.06]),
        elbow + np.array([-0.30, +0.03, s * 0.09]),
    ], max_width=0.042, max_thick=0.018, width_dir=(0, 1, 0), res=4, fixed_joint=3, root_scale=0.5))
    for z_off in (-0.042, 0.0, +0.042):
        t_base = palm + np.array([0.0, -0.01, z_off])
        t_mid = t_base + np.array([0.10, -0.03, z_off * 1.25])
        t_tip = t_mid + np.array([0.08, -0.06, z_off * 1.45])
        add_mesh(4, *build_sculpted_tube(
            [t_base, t_mid, t_tip],
            0.019, 0.003, sides=7, res=4, fixed_joint=3, bulge=0.05
        ))

# Two-Pronged Flame Tail Fin at the tail tip (Bone 9)
tail_root, _, _ = spine_at(SPINE_X[0])
add_mesh(1, *build_3d_plume([
    tail_root + np.array([+0.16, +0.01, 0.0]),
    tail_root + np.array([-0.18, -0.04, 0.0]),
    tail_root + np.array([-0.50, +0.03, 0.0]),
    tail_root + np.array([-0.78, +0.18, 0.0]),
], max_width=0.082, max_thick=0.032, width_dir=(0, 1, 0), res=7, fixed_joint=9, root_scale=0.55))

add_mesh(0, *build_3d_plume([
    tail_root + np.array([+0.08, -0.01, 0.0]),
    tail_root + np.array([-0.24, -0.06, 0.02]),
    tail_root + np.array([-0.56, -0.02, 0.03]),
], max_width=0.054, max_thick=0.024, width_dir=(0, 1, 0), res=6, fixed_joint=9, root_scale=0.55))

add_mesh(3, *build_3d_plume([
    tail_root + np.array([+0.05, +0.02, -0.01]),
    tail_root + np.array([-0.26, +0.03, -0.02]),
    tail_root + np.array([-0.60, +0.14, -0.02]),
], max_width=0.044, max_thick=0.020, width_dir=(0, 1, 0), res=5, fixed_joint=9, root_scale=0.50))


# ---------------------------------------------------------------------------
# 7. Normals, Accessors & Approved KIOKU Linear/sRGB Balanced Palette
# ---------------------------------------------------------------------------
def compute_normals(v: np.ndarray, f: np.ndarray) -> np.ndarray:
    n = np.zeros_like(v, dtype=np.float64)
    tris = v[f]
    cross = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    np.add.at(n, f[:, 0], cross)
    np.add.at(n, f[:, 1], cross)
    np.add.at(n, f[:, 2], cross)
    lengths = np.linalg.norm(n, axis=1)
    n /= np.maximum(lengths[:, None], 1e-9)
    return n.astype('<f4')


def append_accessor(arr: np.ndarray, kind: str, comp: int, target: int | None = None) -> int:
    arr = np.ascontiguousarray(arr, dtype=D[comp])
    count = arr.shape[0]
    while len(raw) % 4:
        raw.append(0)
    start = len(raw)
    raw.extend(arr.tobytes())
    view = {'buffer': 0, 'byteOffset': start, 'byteLength': arr.nbytes}
    if target is not None:
        view['target'] = target
    vi = len(gltf['bufferViews'])
    gltf['bufferViews'].append(view)
    acc = {'bufferView': vi, 'componentType': comp, 'count': count, 'type': kind}
    if kind == 'VEC3' and comp == 5126:
        acc['min'] = arr.min(axis=0).astype(float).tolist()
        acc['max'] = arr.max(axis=0).astype(float).tolist()
    elif kind == 'SCALAR' and comp == 5126:
        acc['min'] = [float(arr.min())]
        acc['max'] = [float(arr.max())]
    ai = len(gltf['accessors'])
    gltf['accessors'].append(acc)
    return ai


gltf['skins'][0]['inverseBindMatrices'] = append_accessor(inv_bind_arr, 'MAT4', 5126)

total_verts = 0
total_tris = 0
for i, prim in enumerate(gltf['meshes'][0]['primitives']):
    b = prims_data[i]
    V = np.concatenate(b['V'], axis=0).astype('<f4')
    F = np.concatenate(b['F'], axis=0).astype(np.int32)
    J = np.concatenate(b['J'], axis=0).astype('<u2')
    W = np.concatenate(b['W'], axis=0).astype('<f4')
    assert len(V) < 65535, f"Primitive {i} exceeds 65535 vertices: {len(V)}"
    assert np.allclose(W.sum(axis=1), 1.0, atol=1e-3)
    assert np.all(W[:, 2:] == 0.0)
    NN = compute_normals(V, F)
    attrs = prim['attributes']
    attrs['POSITION'] = append_accessor(V, 'VEC3', 5126, 34962)
    attrs['NORMAL'] = append_accessor(NN, 'VEC3', 5126, 34962)
    attrs['JOINTS_0'] = append_accessor(J, 'VEC4', 5123, 34962)
    attrs['WEIGHTS_0'] = append_accessor(W, 'VEC4', 5126, 34962)
    prim['indices'] = append_accessor(F.reshape(-1, 1).astype('<u2'), 'SCALAR', 5123, 34963)
    total_verts += len(V)
    total_tris += len(F)

# True linear RGB values matching the approved KIOKU brand artwork (#285078, #14264a, #c8dce6, #5e8f9e, #1e3863, #eef6fa)
approved_materials = {
    0: ([0.032, 0.095, 0.225, 1.0], 0.04, 0.52),  # KIOKU · river blue (#2a527e)
    1: ([0.008, 0.022, 0.076, 1.0], 0.02, 0.62),  # KIOKU · deep outline (#14264c)
    2: ([0.580, 0.720, 0.795, 1.0], 0.02, 0.40),  # KIOKU · mist highlight (#c8dce6)
    3: ([0.115, 0.275, 0.350, 1.0], 0.03, 0.48),  # KIOKU · muted teal (#5e8f9e)
    4: ([0.015, 0.045, 0.130, 1.0], 0.06, 0.46),  # KIOKU · slate-navy horn/talon (#1e3863)
    5: ([0.860, 0.925, 0.960, 1.0], 0.01, 0.25),  # KIOKU · eye accent (#eef6fa)
}
for i, mat in enumerate(gltf['materials']):
    color, metallic, roughness = approved_materials[i]
    pbr = mat.setdefault('pbrMetallicRoughness', {})
    pbr['baseColorFactor'] = color
    pbr['metallicFactor'] = metallic
    pbr['roughnessFactor'] = roughness
    mat['doubleSided'] = True

# Seamless 6-second swimming animation across the 9 body/tail joints
for ch in gltf['animations'][0]['channels']:
    if ch['target']['path'] != 'rotation':
        continue
    joint = ch['target']['node']
    assert 1 <= joint <= 9
    sampler = gltf['animations'][0]['samplers'][ch['sampler']]
    ts = get_acc(sampler['input']).reshape(-1)
    amp = [0.0, 0.026, 0.042, 0.058, 0.072, 0.086, 0.098, 0.110, 0.120, 0.128][joint]
    quats = []
    for t in ts:
        phase = TAU * (float(t) / 6.0) - (joint - 1) * 0.42
        bend_z = amp * math.sin(phase)
        yaw_y = 0.55 * amp * math.cos(phase + 0.25)
        twist_x = 0.15 * amp * math.sin(phase - 0.35)
        cx, sx = math.cos(twist_x * 0.5), math.sin(twist_x * 0.5)
        cy, sy = math.cos(yaw_y * 0.5), math.sin(yaw_y * 0.5)
        cz, sz = math.cos(bend_z * 0.5), math.sin(bend_z * 0.5)
        qx = sx * cy * cz + cx * sy * sz
        qy = cx * sy * cz - sx * cy * sz
        qz = cx * cy * sz + sx * sy * cz
        qw = cx * cy * cz - sx * sy * sz
        norm = math.hypot(qx, qy, qz, qw) or 1.0
        quats.append([qx / norm, qy / norm, qz / norm, qw / norm])
    q_arr = np.array(quats, dtype='<f4')
    q_arr[-1] = q_arr[0]
    acc = gltf['accessors'][sampler['output']]
    view = gltf['bufferViews'][acc['bufferView']]
    base = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    raw[base:base + q_arr.nbytes] = q_arr.tobytes()

gltf['animations'][0]['name'] = 'River Guardian V6 Longform — Production Sculpt 6s Swim'
gltf['asset'].setdefault('extras', {})['KIOKU_PRODUCTION_3D'] = {
    'blender_version': bpy.app.version_string,
    'vertices': int(total_verts),
    'triangles': int(total_tris),
    'bones': 10,
    'materials': 6,
    'animation_tracks': 9,
    'duration_seconds': 6.0,
}


def save_compact_glb(out_path: Path):
    cache = {}
    newbin = bytearray()
    newviews = []
    newacc = []

    def use(idx: int) -> int:
        if idx in cache:
            return cache[idx]
        a = gltf['accessors'][idx]
        v = gltf['bufferViews'][a['bufferView']]
        n = N[a['type']]
        size = D[a['componentType']].itemsize
        start = v.get('byteOffset', 0) + a.get('byteOffset', 0)
        chunk = raw[start:start + a['count'] * n * size]
        while len(newbin) % 4:
            newbin.append(0)
        off = len(newbin)
        newbin.extend(chunk)
        v_idx = len(newviews)
        nv = {'buffer': 0, 'byteOffset': off, 'byteLength': len(chunk)}
        if 'target' in v:
            nv['target'] = v['target']
        newviews.append(nv)
        na = {k: val for k, val in a.items() if k not in ('bufferView', 'byteOffset')}
        na['bufferView'] = v_idx
        a_idx = len(newacc)
        newacc.append(na)
        cache[idx] = a_idx
        return a_idx

    for mesh in gltf['meshes']:
        for pr in mesh['primitives']:
            pr['attributes'] = {k: use(val) for k, val in pr['attributes'].items()}
            pr['indices'] = use(pr['indices'])
    for sk in gltf['skins']:
        sk['inverseBindMatrices'] = use(sk['inverseBindMatrices'])
    for anim in gltf['animations']:
        for s in anim['samplers']:
            s['input'] = use(s['input'])
            s['output'] = use(s['output'])
    gltf['accessors'] = newacc
    gltf['bufferViews'] = newviews
    gltf['buffers'][0]['byteLength'] = len(newbin)
    jb = json.dumps(gltf, ensure_ascii=False, separators=(',', ':')).encode('utf8')
    jb += b' ' * ((-len(jb)) % 4)
    newbin += b'\0' * ((-len(newbin)) % 4)
    total = 12 + 8 + len(jb) + 8 + len(newbin)
    out_path.write_bytes(
        struct.pack('<4sII', b'glTF', 2, total)
        + struct.pack('<I4s', len(jb), b'JSON') + jb
        + struct.pack('<I4s', len(newbin), b'BIN\0') + newbin
    )


save_compact_glb(OUT_GLB)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT_GLB))
scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 180
scene.frame_set(1)

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = True
    elif obj.type == 'ARMATURE':
        obj.show_in_front = True
        obj.display_type = 'WIRE'
        obj.data.display_type = 'OCTAHEDRAL'

OUT_BLEND.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND), compress=True)

print(json.dumps({
    'status': 'OK',
    'blender': bpy.app.version_string,
    'out_glb': str(OUT_GLB),
    'out_blend': str(OUT_BLEND),
    'glb_bytes': OUT_GLB.stat().st_size,
    'vertices': int(total_verts),
    'triangles': int(total_tris),
}, indent=2))
