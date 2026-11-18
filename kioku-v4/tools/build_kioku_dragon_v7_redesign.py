#!/usr/bin/env python3
"""KIOKU River Guardian — Major Brand-Fidelity 3D Redesign + Codex Motion Restoration.

Built natively in Blender 5.3 (Z-up: X=tail-to-head, Y=left-right, Z=UP):
- Redesigned East Asian river dragon head: angular overhanging brow ridges, deep-set
  recessed orbital sockets, sharp upturned almond eyes, sculpted nasal bridge with
  flared nostrils, recessed mouth cleft, defined lower jaw & cheek flow.
- Redesigned flame mane & stag antlers: sculpted diamond/faceted bmesh swept ribbons
  with S-curved flame tips (no round cones or radial spikes), broad-rooted Y-forked
  deep-navy antlers + swept muted-teal secondary horns.
- 3D stylized scale rhythm & body surface language: sculpted imbricated flank scale
  relief, overlapping pale-ice ventral belly scutes (no harsh zebra rings), and
  continuous flowing dorsal neck/arch flame tufts.
- Redesigned 4 articulated dragon legs: muscular shoulder/hip collars, clear elbow/knee
  & wrist joints, elbow flame plumes, and 4 articulated 2-segment clawed digits.
- Restored Codex V6 fluid 6-second traveling-wave swimming animation: unrotated aligned
  10-bone armature, 91 keyframes (15 Hz, 0.00s..6.00s), head anchored, progressive
  phase-delayed wave with natural tail whip follow-through.
"""
from __future__ import annotations
import json, math, struct
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector, Euler, Quaternion

ROOT = Path(__file__).resolve().parents[1]
OUT_GLB = ROOT / 'assets' / 'models' / 'kioku-river-guardian-v6-longform.glb'
OUT_BLEND = ROOT / 'assets' / 'models' / 'kioku-river-guardian-production.blend'

PI = math.pi
TAU = 2.0 * PI

# ---------------------------------------------------------------------------
# 0. Spine & Anatomical Proportions (Blender Z-up, Matched to KIOKU Artwork)
# ---------------------------------------------------------------------------
SPINE_X = [-5.25, -4.60, -3.90, -3.15, -2.35, -1.55, -0.75, +0.05, +0.55, +1.00, +1.42, +1.82, +2.10]
SPINE_Z = [-0.44, -0.20, +0.36, +0.94, +1.15, +0.76, -0.04, -0.62, -0.45, +0.30, +0.84, +0.76, +0.66]
SPINE_Y = [-0.02, -0.04, -0.03, +0.00, +0.04, +0.04, +0.01, -0.03, -0.04, -0.02, +0.00, +0.01, +0.00]
# Muscular chest/neck tapering gracefully to a whip tail
SPINE_RZ = [0.024, 0.056, 0.118, 0.184, 0.232, 0.248, 0.254, 0.262, 0.260, 0.248, 0.236, 0.242, 0.246]
SPINE_RY = [0.022, 0.052, 0.110, 0.172, 0.218, 0.232, 0.238, 0.246, 0.244, 0.232, 0.220, 0.228, 0.236]

BONE_WORLD_X = [2.02, 1.40, 0.72, 0.02, -0.78, -1.58, -2.38, -3.18, -3.98, -4.75]


def catmull_1d(xp, yp, x_eval):
    x_eval = max(xp[0], min(xp[-1], float(x_eval)))
    i = 0
    while i < len(xp) - 2 and xp[i + 1] < x_eval:
        i += 1
    t = (x_eval - xp[i]) / max(1e-8, xp[i + 1] - xp[i])
    p0 = yp[max(0, i - 1)]
    p1 = yp[i]
    p2 = yp[i + 1]
    p3 = yp[min(len(yp) - 1, i + 2)]
    return 0.5 * (
        (2.0 * p1)
        + (-p0 + p2) * t
        + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t * t
        + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t * t * t
    )


def spine_at(x: float):
    p = Vector((x, catmull_1d(SPINE_X, SPINE_Y, x), catmull_1d(SPINE_X, SPINE_Z, x)))
    return p, catmull_1d(SPINE_X, SPINE_RZ, x), catmull_1d(SPINE_X, SPINE_RY, x)


def spine_frame(x: float):
    dx = 0.02
    p0, _, _ = spine_at(max(SPINE_X[0], x - dx))
    p1, _, _ = spine_at(min(SPINE_X[-1], x + dx))
    tan = (p1 - p0).normalized()
    up = Vector((0.0, 1.0, 0.0)).cross(tan)
    if up.length < 1e-5:
        up = Vector((0.0, 0.0, 1.0))
    else:
        up.normalize()
    if up.z < 0:
        up = -up
    side = tan.cross(up).normalized()
    return tan, up, side


def catmull_vec(anchors, res: int = 8):
    pts = [Vector(a) for a in anchors]
    out = []
    for i in range(len(pts) - 1):
        p0 = pts[max(0, i - 1)]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[min(len(pts) - 1, i + 2)]
        for j in range(res):
            t = j / float(res)
            pt = 0.5 * (
                (2.0 * p1)
                + (-p0 + p2) * t
                + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * (t * t)
                + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * (t * t * t)
            )
            out.append(pt)
    out.append(pts[-1])
    return out


# ---------------------------------------------------------------------------
# 1. Initialize Clean Blender Scene & Approved KIOKU Materials
# ---------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 0
scene.frame_end = 180
scene.frame_set(0)

MAT_SPECS = [
    ('KIOKU · river blue',     (0.019, 0.078, 0.198, 1.0), 0.04, 0.50),  # 0: Cobalt river-blue
    ('KIOKU · deep outline',   (0.004, 0.014, 0.054, 1.0), 0.02, 0.60),  # 1: Deep midnight-navy
    ('KIOKU · mist highlight', (0.578, 0.716, 0.791, 1.0), 0.02, 0.42),  # 2: Pale ice-blue belly/jaw
    ('KIOKU · muted teal',     (0.145, 0.355, 0.445, 1.0), 0.03, 0.46),  # 3: Glacier-teal accents
    ('KIOKU · horn bronze',    (0.012, 0.034, 0.112, 1.0), 0.05, 0.44),  # 4: Slate-navy horn/talons
    ('KIOKU · eye accent',     (0.865, 0.930, 0.962, 1.0), 0.01, 0.22),  # 5: Crisp ice-white sclera
]

materials = []
for name, col, met, rough in MAT_SPECS:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = col
    bsdf.inputs['Metallic'].default_value = met
    bsdf.inputs['Roughness'].default_value = rough
    materials.append(m)


def finalize_bmesh_obj(name: str, bm: bmesh.types.BMesh, subsurf: int = 0):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    scene.collection.objects.link(obj)
    for m in materials:
        obj.data.materials.append(m)
    for p in obj.data.polygons:
        p.use_smooth = True
    if subsurf > 0:
        mod = obj.modifiers.new('Subsurf', 'SUBSURF')
        mod.levels = subsurf
        mod.render_levels = subsurf
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


# ---------------------------------------------------------------------------
# 2. Custom BMesh Sculpted Builders (Flame Blades, Fluted Antlers, Limbs)
# ---------------------------------------------------------------------------
def build_sculpted_flame_lock(name: str, anchors, width_fn, thick_fn, width_dir=(0, 0, 1), mat_idx: int = 1, res: int = 6):
    """Sculpted 8-sided faceted flame blade with raised center ridge and curled tip."""
    pts = catmull_vec(anchors, res=res)
    n = len(pts)
    w_ref = Vector(width_dir).normalized()
    bm = bmesh.new()
    rings = []
    # 8-point sculpted blade cross-section: top sharp edge, upper bevels, thick ridge, lower bevels, bottom edge
    sec_coords = [
        (1.00, 0.00),
        (0.55, 0.72),
        (0.00, 1.00),
        (-0.55, 0.72),
        (-1.00, 0.00),
        (-0.55, -0.72),
        (0.00, -1.00),
        (0.55, -0.72),
    ]
    for i, p in enumerate(pts):
        u = i / max(1, n - 1)
        w = width_fn(u)
        th = thick_fn(u)
        tan = (pts[min(n - 1, i + 1)] - pts[max(0, i - 1)]).normalized()
        across = w_ref - w_ref.dot(tan) * tan
        if across.length < 1e-5:
            across = Vector((0, 0, 1)) if abs(tan.z) < 0.9 else Vector((0, 1, 0))
        else:
            across.normalize()
        thick_ax = tan.cross(across).normalized()
        ring = []
        for aw, at in sec_coords:
            ring.append(bm.verts.new(p + across * (aw * w) + thick_ax * (at * th)))
        rings.append(ring)

    cols = len(sec_coords)
    for i in range(n - 1):
        for k in range(cols):
            kn = (k + 1) % cols
            f = bm.faces.new((rings[i][k], rings[i + 1][k], rings[i + 1][kn], rings[i][kn]))
            f.material_index = mat_idx

    # Close root & pointed tip cleanly
    root_c = bm.verts.new(pts[0])
    tip_c = bm.verts.new(pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.012)
    for k in range(cols):
        kn = (k + 1) % cols
        bm.faces.new((rings[0][kn], rings[0][k], root_c)).material_index = mat_idx
        bm.faces.new((rings[-1][k], rings[-1][kn], tip_c)).material_index = mat_idx
    return finalize_bmesh_obj(name, bm)


def build_fluted_horn(name: str, anchors, r_fn, mat_idx: int = 1, tip_mat_idx: int | None = None, sides: int = 10, res: int = 7, flutes: int = 5):
    """Organic fluted stag-antler/horn mesh with flared skull burr and curved taper."""
    pts = catmull_vec(anchors, res=res)
    n = len(pts)
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(pts):
        u = i / max(1, n - 1)
        r = r_fn(u)
        tan = (pts[min(n - 1, i + 1)] - pts[max(0, i - 1)]).normalized()
        ref = Vector((0, 1, 0)) if abs(tan.y) < 0.88 else Vector((0, 0, 1))
        side = tan.cross(ref).normalized()
        up = side.cross(tan).normalized()
        ring = []
        for q in range(sides):
            ang = TAU * q / sides
            flute = 1.0 + 0.09 * math.cos(flutes * ang) * (1.0 - 0.6 * u)
            # Slightly oval anteroposterior cross-section
            pt = p + up * (math.cos(ang) * r * 1.12 * flute) + side * (math.sin(ang) * r * 0.88 * flute)
            ring.append(bm.verts.new(pt))
        rings.append(ring)

    for i in range(n - 1):
        u = i / max(1, n - 1)
        m_i = tip_mat_idx if (tip_mat_idx is not None and u > 0.65) else mat_idx
        for q in range(sides):
            qn = (q + 1) % sides
            f = bm.faces.new((rings[i][q], rings[i + 1][q], rings[i + 1][qn], rings[i][qn]))
            f.material_index = m_i

    root_c = bm.verts.new(pts[0])
    tip_c = bm.verts.new(pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.008)
    for q in range(sides):
        qn = (q + 1) % sides
        bm.faces.new((rings[0][qn], rings[0][q], root_c)).material_index = mat_idx
        bm.faces.new((rings[-1][q], rings[-1][qn], tip_c)).material_index = tip_mat_idx if tip_mat_idx is not None else mat_idx
    return finalize_bmesh_obj(name, bm)


# ---------------------------------------------------------------------------
# 3. Phase B.D — Serpentine Body with 3D Scale Relief & Overlapping Belly Scutes
# ---------------------------------------------------------------------------
def build_body_with_scales():
    bm = bmesh.new()
    rings = 196
    cols = 36
    xs = [SPINE_X[0] + (SPINE_X[-1] - SPINE_X[0]) * i / (rings - 1) for i in range(rings)]
    grid = []
    for i, x in enumerate(xs):
        c, rz, ry = spine_at(x)
        _, up, side = spine_frame(x)
        # Fade scale relief cleanly near tip of tail
        scale_env = max(0.0, min(1.0, (x - (-4.55)) / 1.20))
        ring = []
        for k in range(cols):
            ang = TAU * k / cols  # 0 = top dorsal (+up), PI = bottom belly (-up)
            ca, sa = math.cos(ang), math.sin(ang)
            ang_s = ang if ang <= PI else ang - TAU
            abs_ang = abs(ang_s)
            rmod = 1.0

            # 1. Sculpted dorsal ridge crest
            if abs_ang < 0.42:
                rmod += 0.095 * math.exp(-((abs_ang / 0.20) ** 2))

            # 2. 3D stylized imbricated scale relief on cobalt flanks (0.58 < |ang| < 2.05)
            if 0.58 < abs_ang < 2.08 and scale_env > 0.01:
                row_idx = int((abs_ang - 0.58) / 0.30)
                phase_x = (x + 5.2) / 0.22 + (0.5 if row_idx % 2 else 0.0)
                saw = phase_x - math.floor(phase_x)
                scale_lift = (saw ** 1.5) * (1.0 if saw < 0.85 else (1.0 - saw) / 0.15)
                row_bell = math.sin(PI * ((abs_ang - 0.58) % 0.30) / 0.30) ** 0.65
                rmod += 0.068 * scale_env * scale_lift * row_bell

            # 3. Overlapping pale-ice belly scute plates (|ang| > 2.15) — physical stepped overlap
            if abs_ang > 2.12:
                scute_u = ((x + 5.2) / 0.32) % 1.0
                scute_step = 0.036 * (1.0 - scute_u) if scute_u > 0.09 else -0.032
                rmod *= 0.94 + scute_step
                rmod *= 1.0 - 0.05 * math.exp(-(((abs_ang - PI) / 0.55) ** 2))

            pt = c + up * (ca * rz * rmod) + side * (sa * ry * rmod)
            ring.append(bm.verts.new(pt))
        grid.append(ring)

    bm.verts.ensure_lookup_table()
    for i in range(rings - 1):
        xm = 0.5 * (xs[i] + xs[i + 1])
        scute_u = ((xm + 5.2) / 0.32) % 1.0
        is_scute_seam = scute_u < 0.055
        for k in range(cols):
            kn = (k + 1) % cols
            f = bm.faces.new((grid[i][k], grid[i + 1][k], grid[i + 1][kn], grid[i][kn]))
            ang_m = TAU * ((k + 0.5) / cols)
            if ang_m > PI:
                ang_m -= TAU
            abs_m = abs(ang_m)
            if abs_m < 0.68:
                f.material_index = 1  # Deep-navy dorsal back
            elif abs_m > 2.16:
                f.material_index = 3 if is_scute_seam else 2  # Soft glacier-teal scute crease (no harsh black zebra bands)
            else:
                f.material_index = 0  # Sculpted river-blue scale flanks

    tail_tip = bm.verts.new(spine_at(SPINE_X[0])[0] + Vector((-0.05, 0.0, -0.01)))
    for k in range(cols):
        bm.faces.new((grid[0][(k + 1) % cols], grid[0][k], tail_tip)).material_index = 1

    return finalize_bmesh_obj('KIOKU_Body', bm)


# ---------------------------------------------------------------------------
# 4. Phase B.A — Redesigned East Asian River Dragon Head
# ---------------------------------------------------------------------------
def build_dragon_head():
    objs = []

    # A. Sculpted Dragon Skull + Upper Muzzle + Separate Lower Jaw with Recessed Mouth Cleft
    # 15 axial profiles from occiput/nape (x=1.88) to upturned snout tip (x=3.34)
    bm = bmesh.new()
    hx     = [1.88, 2.02, 2.16, 2.30, 2.44, 2.58, 2.70, 2.82, 2.94, 3.06, 3.16, 3.24, 3.31, 3.35]
    hz_top = [0.89, 0.95, 1.01, 1.04, 1.02, 0.96, 0.91, 0.89, 0.90, 0.92, 0.95, 0.96, 0.93, 0.87]
    hz_bot = [0.42, 0.38, 0.36, 0.36, 0.38, 0.43, 0.49, 0.55, 0.61, 0.66, 0.70, 0.73, 0.76, 0.79]
    hry    = [0.24, 0.28, 0.32, 0.33, 0.29, 0.24, 0.20, 0.17, 0.15, 0.14, 0.13, 0.11, 0.08, 0.04]
    cols = 32
    grid = []
    for i, x in enumerate(hx):
        cz = 0.5 * (hz_top[i] + hz_bot[i])
        rz = 0.5 * (hz_top[i] - hz_bot[i])
        ry = hry[i]
        ring = []
        for k in range(cols):
            ang = TAU * k / cols  # 0=crown, PI/2=right cheek, PI=chin, -PI/2=left cheek
            ca, sa = math.cos(ang), math.sin(ang)
            ang_s = ang if ang <= PI else ang - TAU
            abs_a = abs(ang_s)

            # Dragon skull squaring: flatter crown & squared muzzle top, tapered cheeks
            z_off = ca * rz
            y_off = sa * ry

            # 1. Strong overhanging angular dragon brow ridge (x in [2.32, 2.86], |ang| in [0.48, 1.08])
            if 2.28 <= x <= 2.88:
                brow_env = math.exp(-(((x - 2.56) / 0.18) ** 2))
                brow_a = math.exp(-(((abs_a - 0.78) / 0.25) ** 2))
                z_off += 0.068 * brow_env * brow_a
                y_off += math.copysign(0.056 * brow_env * brow_a, sa)

            # 2. Deeply recessed orbital socket directly under brow (x in [2.42, 2.84], |ang| in [1.10, 1.58])
            if 2.40 <= x <= 2.86 and 1.06 <= abs_a <= 1.60:
                sock_env = math.exp(-(((x - 2.63) / 0.14) ** 2)) * math.sin(PI * (abs_a - 1.06) / 0.54)
                y_off *= (1.0 - 0.26 * sock_env)

            # 3. Sculpted cheekbone & upper lip shelf (|ang| in [1.60, 2.02])
            if 2.26 <= x <= 3.16 and 1.58 <= abs_a <= 2.04:
                lip_env = math.sin(PI * (abs_a - 1.58) / 0.46)
                y_off += math.copysign(0.038 * lip_env, sa)

            # 4. Recessed mouth-cleft seam separating upper lip & lower jaw (|ang| around 2.08..2.26)
            if 2.44 <= x <= 3.26 and 2.02 <= abs_a <= 2.28:
                cleft = math.sin(PI * (abs_a - 2.02) / 0.26)
                y_off *= (1.0 - 0.18 * cleft)

            # 5. Narrower defined lower jaw beneath cleft (|ang| > 2.28)
            if abs_a > 2.28 and x >= 2.36:
                y_off *= 0.86

            # 6. Raised dragon nasal ridge & flared nostril bosses (x >= 2.80)
            if x >= 2.78 and abs_a < 0.45:
                z_off += 0.018 * math.cos(PI * abs_a / 0.90)
            if 3.10 <= x <= 3.30 and 0.42 <= abs_a <= 1.05:
                nos_env = math.exp(-(((x - 3.20) / 0.06) ** 2))
                z_off += 0.032 * nos_env
                y_off += math.copysign(0.032 * nos_env, sa)

            ring.append(bm.verts.new((x, y_off, cz + z_off)))
        grid.append(ring)

    for i in range(len(hx) - 1):
        xm = 0.5 * (hx[i] + hx[i + 1])
        for k in range(cols):
            kn = (k + 1) % cols
            f = bm.faces.new((grid[i][k], grid[i + 1][k], grid[i + 1][kn], grid[i][kn]))
            ang_m = TAU * ((k + 0.5) / cols)
            if ang_m > PI:
                ang_m -= TAU
            abs_m = abs(ang_m)
            # Continuous anatomical material zones matching the approved KIOKU head close-up:
            # - Crown, forehead & brow overhang -> Mat 1 (deep midnight-navy)
            # - Nasal snout bridge (x > 2.74, |ang| < 0.52) -> Mat 3 (muted teal)
            # - Mouth cleft crease -> Mat 1 (deep navy)
            # - Pale under-jaw & chin -> Mat 2 (pale ice-blue)
            # - Cheeks & muzzle sides -> Mat 0 (river blue)
            if abs_m > 2.28:
                f.material_index = 2
            elif xm >= 2.44 and 2.04 <= abs_m <= 2.28:
                f.material_index = 1
            elif xm >= 2.74 and abs_m < 0.52:
                f.material_index = 3
            elif abs_m < 0.92:
                f.material_index = 1
            else:
                f.material_index = 0

    tip_v = bm.verts.new((3.37, 0.0, 0.84))
    for k in range(cols):
        bm.faces.new((grid[-1][k], tip_v, grid[-1][(k + 1) % cols])).material_index = 0

    objs.append(finalize_bmesh_obj('KIOKU_Head', bm, subsurf=1))

    # B. Deep-Set Almond Eyes, Glacier-Teal Cheek Sweep, Nostrils & Chin Beard Tufts
    for s in (-1.0, 1.0):
        # 1. Recessed Almond Eye Sclera tucked cleanly beneath the overhanging dark-navy brow ridge
        objs.append(build_sculpted_flame_lock(
            f'Eye_Sclera_{s:+.0f}',
            [(2.46, s * 0.244, 0.682), (2.58, s * 0.246, 0.716), (2.71, s * 0.220, 0.742), (2.82, s * 0.186, 0.746)],
            width_fn=lambda u: 0.044 * math.sin(PI * u) ** 0.72,
            thick_fn=lambda u: 0.018 * math.sin(PI * u) ** 0.72,
            width_dir=(0, 0, 1), mat_idx=5, res=5
        ))
        # 2. Focused Dark-Navy Iris/Pupil inside the almond eye
        objs.append(build_sculpted_flame_lock(
            f'Eye_Pupil_{s:+.0f}',
            [(2.62, s * 0.258, 0.720), (2.69, s * 0.246, 0.734), (2.75, s * 0.226, 0.740)],
            width_fn=lambda u: 0.032 * math.sin(PI * u) ** 0.65,
            thick_fn=lambda u: 0.020 * math.sin(PI * u) ** 0.65,
            width_dir=(0, 0, 1), mat_idx=1, res=4
        ))
        # 2b. Crisp Deep-Navy Upper Eyelid Crease hugging top of almond eye under brow
        objs.append(build_sculpted_flame_lock(
            f'Eyelid_Crease_{s:+.0f}',
            [(2.44, s * 0.246, 0.692), (2.58, s * 0.250, 0.746), (2.72, s * 0.224, 0.766), (2.84, s * 0.186, 0.752)],
            width_fn=lambda u: 0.018 * math.sin(PI * u) ** 0.65,
            thick_fn=lambda u: 0.014 * math.sin(PI * u) ** 0.65,
            width_dir=(0, 0, 1), mat_idx=1, res=5
        ))
        # 3. Glacier-Teal Lower-Orbital Cheek Highlight Plate (flush along cheekbone under eye)
        objs.append(build_sculpted_flame_lock(
            f'Cheek_Highlight_{s:+.0f}',
            [(2.36, s * 0.258, 0.51), (2.56, s * 0.256, 0.56), (2.78, s * 0.205, 0.62), (3.00, s * 0.150, 0.68)],
            width_fn=lambda u: 0.056 * math.sin(PI * u) ** 0.7,
            thick_fn=lambda u: 0.016 * math.sin(PI * u) ** 0.7,
            width_dir=(0, 0, 1), mat_idx=3, res=5
        ))
        # 4. Sculpted Nostril Hollow behind upturned snout flare
        objs.append(build_fluted_horn(
            f'Nostril_{s:+.0f}',
            [(3.18, s * 0.105, 0.875), (3.24, s * 0.095, 0.885)],
            r_fn=lambda u: 0.015 * (1.0 - 0.3 * u),
            mat_idx=1, sides=8, res=3, flutes=0
        ))

    # 3 Swept-Back Chin Beard Curls (Mat 1) under rear jaw angle
    for i, (tx, tz, tl) in enumerate([(2.44, 0.38, 0.12), (2.28, 0.36, 0.14), (2.12, 0.38, 0.12)]):
        objs.append(build_sculpted_flame_lock(
            f'Chin_Beard_{i}',
            [(tx + 0.05, 0.0, tz + 0.03), (tx - 0.03, 0.0, tz - tl * 0.55), (tx - 0.14, 0.0, tz - tl)],
            width_fn=lambda u: 0.036 * (1.0 - 0.85 * u),
            thick_fn=lambda u: 0.018 * (1.0 - 0.85 * u),
            width_dir=(1, 0, 0), mat_idx=1, res=4
        ))

    return objs


# ---------------------------------------------------------------------------
# 5. Phase B.B & B.C — Redesigned Stag Antlers, Flowing Flame Mane & Whiskers
# ---------------------------------------------------------------------------
def build_horns_mane_whiskers():
    objs = []
    for s in (-1.0, 1.0):
        # A. Main Deep-Navy Stag Antler (broad skull root -> organic sweep back -> graceful upward hook + Y-fork)
        objs.append(build_fluted_horn(
            f'Antler_Main_{s:+.0f}',
            [(2.34, s * 0.11, 0.94), (2.12, s * 0.14, 1.07), (1.84, s * 0.17, 1.24), (1.58, s * 0.19, 1.40), (1.42, s * 0.20, 1.54)],
            r_fn=lambda u: (0.072 if u < 0.08 else 0.056) * (1.0 - 0.88 * u),
            mat_idx=1, tip_mat_idx=4, sides=10, res=7
        ))
        objs.append(build_fluted_horn(
            f'Antler_Fork_{s:+.0f}',
            [(2.00, s * 0.15, 1.14), (2.04, s * 0.17, 1.29), (2.15, s * 0.18, 1.44), (2.30, s * 0.19, 1.55)],
            r_fn=lambda u: 0.038 * (1.0 - 0.86 * u),
            mat_idx=1, tip_mat_idx=4, sides=8, res=6
        ))

        # B. Rear/Outer Muted-Teal Secondary Antler (organic swept-back S-curve + short upward spur)
        objs.append(build_fluted_horn(
            f'Horn_Teal_Main_{s:+.0f}',
            [(2.14, s * 0.16, 0.90), (1.84, s * 0.20, 1.02), (1.52, s * 0.23, 1.15), (1.26, s * 0.25, 1.25)],
            r_fn=lambda u: 0.054 * (1.0 - 0.88 * u),
            mat_idx=3, sides=10, res=7
        ))
        objs.append(build_fluted_horn(
            f'Horn_Teal_Spur_{s:+.0f}',
            [(1.76, s * 0.21, 1.06), (1.60, s * 0.23, 1.20), (1.48, s * 0.24, 1.32)],
            r_fn=lambda u: 0.030 * (1.0 - 0.85 * u),
            mat_idx=3, sides=8, res=5
        ))

        # C. Flowing S-Curved Flame Mane Locks wrapping head/neck with hooked tips (NO stiff cones!)
        mane_specs = [
            # Upper crown lock curling back-up around neck nape
            ([(2.28, s * 0.14, 0.88), (1.96, s * 0.20, 0.94), (1.60, s * 0.23, 0.92), (1.30, s * 0.24, 1.02), (1.14, s * 0.24, 1.12)], 0.088, 0.032, 1),
            # Broad mid-temple flame lock with S-wave flip
            ([(2.32, s * 0.18, 0.76), (1.92, s * 0.24, 0.78), (1.52, s * 0.26, 0.70), (1.18, s * 0.27, 0.76), (1.02, s * 0.27, 0.86)], 0.105, 0.036, 1),
            # Prominent Glacier-Teal cheek/ear highlight curl (signature KIOKU motif!)
            ([(2.34, s * 0.21, 0.62), (1.96, s * 0.26, 0.60), (1.60, s * 0.28, 0.52), (1.28, s * 0.28, 0.56), (1.14, s * 0.27, 0.66)], 0.062, 0.024, 3),
            # Lower cheek flame lock sweeping gracefully along throat
            ([(2.30, s * 0.20, 0.52), (1.90, s * 0.25, 0.46), (1.50, s * 0.26, 0.36), (1.18, s * 0.25, 0.40), (1.04, s * 0.24, 0.48)], 0.095, 0.034, 1),
            # Jaw-angle curl hugging the throat
            ([(2.22, s * 0.16, 0.42), (1.90, s * 0.21, 0.34), (1.58, s * 0.22, 0.25), (1.32, s * 0.21, 0.30)], 0.072, 0.028, 1),
        ]
        for idx_m, (pts, mw, mt, m_i) in enumerate(mane_specs):
            objs.append(build_sculpted_flame_lock(
                f'Mane_Flame_{s:+.0f}_{idx_m}', pts,
                width_fn=lambda u, mw=mw: mw * (0.58 * (1.0 - u) + 0.88 * math.sin(PI * u) ** 0.75) * (1.0 - 0.15 * u),
                thick_fn=lambda u, mt=mt: mt * (0.65 * (1.0 - u) + 0.80 * math.sin(PI * u) ** 0.75),
                width_dir=(0, 0, 1), mat_idx=m_i, res=6
            ))

    # D. Single Pair of Graceful Calligraphy S-Curved Whiskers (Mat 3)
    objs.append(build_fluted_horn(
        'Whisker_Up',
        [(3.18, +0.10, 0.85), (3.44, +0.16, 0.96), (3.68, +0.22, 1.18), (3.82, +0.24, 1.42), (3.68, +0.20, 1.56)],
        r_fn=lambda u: 0.013 * (1.0 - 0.82 * u),
        mat_idx=3, sides=7, res=7, flutes=0
    ))
    objs.append(build_fluted_horn(
        'Whisker_Down',
        [(3.16, -0.10, 0.79), (3.44, -0.16, 0.68), (3.70, -0.22, 0.64), (3.96, -0.24, 0.66), (4.06, -0.20, 0.48)],
        r_fn=lambda u: 0.013 * (1.0 - 0.82 * u),
        mat_idx=3, sides=7, res=7, flutes=0
    ))
    return objs


# ---------------------------------------------------------------------------
# 6. Phase B.D & B.E — Flowing Dorsal Crest, Redesigned 4 Dragon Legs & Tail Fin
# ---------------------------------------------------------------------------
def build_crest_four_legs_tail():
    objs = []

    # A. Continuous Flowing Dorsal Flame Crest (Neck Arch + Rear Arch) matching media_1795013071178_6b177c21.png
    crest_specs = [
        (1.48, 0.40, 0.068),
        (1.22, 0.46, 0.074),
        (0.94, 0.48, 0.072),
        (-1.82, 0.36, 0.058),
        (-2.24, 0.40, 0.062),
        (-2.66, 0.38, 0.058),
        (-3.08, 0.34, 0.050),
    ]
    for idx_c, (xc, length_c, width_c) in enumerate(crest_specs):
        p, rz, _ = spine_at(xc)
        tan, up, _ = spine_frame(xc)
        pts = [
            p + up * (rz * 0.68) + tan * 0.16,
            p + up * (rz + 0.09) - tan * (length_c * 0.32),
            p + up * (rz + 0.13) - tan * (length_c * 0.75),
            p + up * (rz + 0.18) - tan * (length_c * 1.05),
        ]
        objs.append(build_sculpted_flame_lock(
            f'Dorsal_Crest_{idx_c}', pts,
            width_fn=lambda u, wc=width_c: wc * (0.55 * (1.0 - u) + 0.85 * math.sin(PI * u) ** 0.75),
            thick_fn=lambda u, wc=width_c: wc * 0.38 * (0.55 * (1.0 - u) + 0.85 * math.sin(PI * u) ** 0.75),
            width_dir=(0, 0, 1), mat_idx=1, res=5
        ))

    # B. Redesigned 4 Articulated Dragon Limbs (Upper Forelimbs + Lower Hindlimbs)
    # Each limb features: muscular shoulder/hip collar, anatomical taper through elbow/knee
    # and wrist/ankle, sculpted palm/foot pad, elbow flame plume, and 4 articulated 2-segment claws.
    limb_specs = [
        # Upper forelimb on rising chest arch (x = 0.96) reaching gracefully forward & outward
        ('Forelimb', 0.96, (0.0, 0.82, 0.12), (0.28, 0.14, 0.05), (0.54, 0.06, -0.09), (0.68, 0.03, -0.15), 0.96),
        # Lower hindlimb at bottom S-curve trough (x = 0.08) reaching downward & forward
        ('Hindlimb', 0.08, (0.0, 0.82, -0.52), (-0.14, 0.14, -0.28), (0.05, 0.06, -0.50), (0.18, 0.03, -0.56), 1.04),
    ]
    for lname, x_att, sdir, eoff, woff, poff, sc in limb_specs:
        cp, rz, ry = spine_at(x_att)
        for s in (-1.0, 1.0):
            # Collar buried slightly inside torso for seamless attachment
            collar = cp + Vector((-0.02, s * ry * 0.55, sdir[2] * rz * 0.72))
            sh = cp + Vector((0.0, s * ry * sdir[1], sdir[2] * rz))
            el = sh + Vector((eoff[0] * sc, s * eoff[1] * sc, eoff[2] * sc))
            wr = sh + Vector((woff[0] * sc, s * woff[1] * sc, woff[2] * sc))
            pa = sh + Vector((poff[0] * sc, s * poff[1] * sc, poff[2] * sc))

            # Build muscular limb loft with flared shoulder & distinct wrist/palm
            limb_pts = catmull_vec([collar, sh, el, wr, pa], res=6)
            n_l = len(limb_pts)
            bm_l = bmesh.new()
            l_rings = []
            for i, pt in enumerate(limb_pts):
                u = i / max(1, n_l - 1)
                # Flared shoulder -> muscular bicep -> elbow pinch -> tapered forearm -> flared palm
                if u < 0.25:
                    rad = (0.125 - 0.10 * u) * sc
                elif u < 0.55:
                    rad = (0.100 - 0.04 * (u - 0.25) / 0.30) * sc
                elif u < 0.85:
                    rad = (0.060 - 0.018 * (u - 0.55) / 0.30) * sc
                else:
                    rad = (0.042 + 0.014 * math.sin(PI * (u - 0.85) / 0.15)) * sc
                tan = (limb_pts[min(n_l - 1, i + 1)] - limb_pts[max(0, i - 1)]).normalized()
                ref = Vector((0, 1, 0)) if abs(tan.y) < 0.88 else Vector((0, 0, 1))
                side_l = tan.cross(ref).normalized()
                up_l = side_l.cross(tan).normalized()
                ring = []
                for q in range(12):
                    ang = TAU * q / 12
                    ring.append(bm_l.verts.new(pt + up_l * (math.cos(ang) * rad * 1.08) + side_l * (math.sin(ang) * rad * 0.92)))
                l_rings.append(ring)
            for i in range(n_l - 1):
                for q in range(12):
                    qn = (q + 1) % 12
                    bm_l.faces.new((l_rings[i][q], l_rings[i + 1][q], l_rings[i + 1][qn], l_rings[i][qn])).material_index = 0
            palm_tip = bm_l.verts.new(pa + (pa - wr).normalized() * 0.03)
            for q in range(12):
                bm_l.faces.new((l_rings[-1][q], l_rings[-1][(q + 1) % 12], palm_tip)).material_index = 0
            objs.append(finalize_bmesh_obj(f'{lname}_{s:+.0f}', bm_l))

            # Swept-back elbow flame plume (Mat 1)
            objs.append(build_sculpted_flame_lock(
                f'{lname}_ElbowPlume_{s:+.0f}',
                [el + Vector((0.02, 0.0, 0.0)), el + Vector((-0.18 * sc, s * 0.05 * sc, -0.01 * sc)), el + Vector((-0.36 * sc, s * 0.09 * sc, 0.05 * sc))],
                width_fn=lambda u, sc=sc: 0.044 * sc * (0.55 * (1.0 - u) + 0.8 * math.sin(PI * u)),
                thick_fn=lambda u, sc=sc: 0.018 * sc * (0.55 * (1.0 - u) + 0.8 * math.sin(PI * u)),
                width_dir=(0, 0, 1), mat_idx=1, res=4
            ))

            # 4 Articulated 2-Segment Dragon Digits + Curved Talons (Mat 0 digit -> Mat 4 talon tip)
            digit_angles = [(0.045, -0.055), (0.018, -0.018), (-0.012, 0.018), (-0.042, 0.055)]
            for ci, (dz, dy) in enumerate(digit_angles):
                d0 = pa + Vector((0.0, s * dy * 0.4 * sc, dz * 0.4 * sc))
                d1 = d0 + Vector((0.065 * sc, s * dy * 0.9 * sc, dz * 0.9 * sc + 0.015 * sc))
                d2 = d1 + Vector((0.065 * sc, s * dy * 1.1 * sc, dz * 0.7 * sc - 0.025 * sc))
                d3 = d2 + Vector((0.055 * sc, s * dy * 1.1 * sc, dz * 0.4 * sc - 0.055 * sc))
                objs.append(build_fluted_horn(
                    f'{lname}_Digit_{s:+.0f}_{ci}', [d0, d1, d2, d3],
                    r_fn=lambda u, sc=sc: 0.022 * sc * (1.0 - 0.82 * u),
                    mat_idx=0, tip_mat_idx=4, sides=8, res=4, flutes=0
                ))

    # C. Multi-Layered Forked Flame Tail Fin (distinct 3-plume swept silhouette!)
    t_root, _, _ = spine_at(SPINE_X[0])
    objs.append(build_sculpted_flame_lock(
        'Tail_Fin_Upper',
        [t_root + Vector((0.12, 0.0, 0.01)), t_root + Vector((-0.24, 0.0, 0.02)), t_root + Vector((-0.58, 0.0, 0.16)), t_root + Vector((-0.86, 0.0, 0.34))],
        width_fn=lambda u: 0.068 * (0.45 * (1.0 - u) + 0.90 * math.sin(PI * u) ** 0.75),
        thick_fn=lambda u: 0.022 * (0.45 * (1.0 - u) + 0.90 * math.sin(PI * u) ** 0.75),
        width_dir=(0, 0, 1), mat_idx=1, res=6
    ))
    objs.append(build_sculpted_flame_lock(
        'Tail_Fin_Mid',
        [t_root + Vector((0.08, 0.0, 0.00)), t_root + Vector((-0.28, 0.02, -0.02)), t_root + Vector((-0.66, 0.02, 0.06))],
        width_fn=lambda u: 0.052 * (0.45 * (1.0 - u) + 0.88 * math.sin(PI * u) ** 0.75),
        thick_fn=lambda u: 0.018 * (0.45 * (1.0 - u) + 0.88 * math.sin(PI * u) ** 0.75),
        width_dir=(0, 0, 1), mat_idx=0, res=5
    ))
    objs.append(build_sculpted_flame_lock(
        'Tail_Fin_Teal_Lower',
        [t_root + Vector((0.06, -0.01, -0.01)), t_root + Vector((-0.28, -0.02, -0.06)), t_root + Vector((-0.64, -0.02, -0.02))],
        width_fn=lambda u: 0.044 * (0.45 * (1.0 - u) + 0.88 * math.sin(PI * u) ** 0.75),
        thick_fn=lambda u: 0.016 * (0.45 * (1.0 - u) + 0.88 * math.sin(PI * u) ** 0.75),
        width_dir=(0, 0, 1), mat_idx=3, res=5
    ))
    return objs


# ---------------------------------------------------------------------------
# 7. Join Mesh, Bind Aligned 10-Bone Rig & Restore Codex 6s Fluid Traveling Wave
# ---------------------------------------------------------------------------
all_parts = [build_body_with_scales()] + build_dragon_head() + build_horns_mane_whiskers() + build_crest_four_legs_tail()
bpy.ops.object.select_all(action='DESELECT')
for o in all_parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = all_parts[0]
bpy.ops.object.join()
dragon_obj = bpy.context.active_object
dragon_obj.name = 'KIOKU_River_Guardian_Mesh'

# Build 10-bone Armature with UNROTATED aligned rest frames (tail = head + (-0.45, 0, 0))
# so every joint's local axes stay aligned to world axes, eliminating twisted/wrenched motion!
arm_data = bpy.data.armatures.new('KIOKU_River_Guardian_Rig')
arm_data.display_type = 'OCTAHEDRAL'
arm_obj = bpy.data.objects.new('KIOKU_River_Guardian_Rig', arm_data)
arm_obj.show_in_front = True
scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

bone_names = [
    'RG_Bone_00_HEAD', 'RG_Bone_01_BODY', 'RG_Bone_02_BODY', 'RG_Bone_03_BODY',
    'RG_Bone_04_BODY', 'RG_Bone_05_BODY', 'RG_Bone_06_BODY', 'RG_Bone_07_BODY',
    'RG_Bone_08_BODY', 'RG_Bone_09_TAIL'
]
ebones = []
for i, bname in enumerate(bone_names):
    eb = arm_data.edit_bones.new(bname)
    head_p, _, _ = spine_at(BONE_WORLD_X[i])
    eb.head = head_p
    eb.tail = head_p + Vector((-0.45, 0.0, 0.0))
    eb.roll = 0.0
    if i > 0:
        eb.parent = ebones[i - 1]
        eb.use_connect = False
    eb.use_deform = True
    ebones.append(eb)
bpy.ops.object.mode_set(mode='OBJECT')

# Smoothstep 2-bone vertex weights (WebGL1 compatible)
vgroups = [dragon_obj.vertex_groups.new(name=bn) for bn in bone_names]
for v in dragon_obj.data.vertices:
    x = v.co.x
    if x >= BONE_WORLD_X[0]:
        vgroups[0].add([v.index], 1.0, 'REPLACE')
    elif x <= BONE_WORLD_X[-1]:
        vgroups[9].add([v.index], 1.0, 'REPLACE')
    else:
        for i in range(9):
            if BONE_WORLD_X[i] >= x >= BONE_WORLD_X[i + 1]:
                u = (BONE_WORLD_X[i] - x) / max(1e-8, BONE_WORLD_X[i] - BONE_WORLD_X[i + 1])
                s = u * u * (3.0 - 2.0 * u)
                vgroups[i].add([v.index], 1.0 - s, 'REPLACE')
                vgroups[i + 1].add([v.index], s, 'REPLACE')
                break

dragon_obj.parent = arm_obj
arm_mod = dragon_obj.modifiers.new('Armature', 'ARMATURE')
arm_mod.object = arm_obj

# Restore Codex V6 fluid 91-keyframe (15 Hz) traveling wave over 0.00s..6.00s:
# - Head (Bone 0) stays anchored/stable
# - Smooth progressive phase delay (-0.52 rad per bone) + supple mid-body + tail follow-through
# - Note: Blender Z-up bone aligned along -X maps:
#     local X rotation -> roll around spine
#     local Y rotation -> vertical S-wave pitch
#     local Z rotation -> horizontal lateral swing
arm_obj.animation_data_create()
action = bpy.data.actions.new('KIOKU River Guardian V6 Longform — Codex Motion 6s Swim')
arm_obj.animation_data.action = action
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

# Matched to Codex PR #10 / V4 motion benchmark (peak deg per joint: ~4..14 deg)
AMP_VERT = [0.0, 0.055, 0.085, 0.110, 0.095, 0.080, 0.095, 0.115, 0.140, 0.220]
AMP_LAT  = [0.0, 0.022, 0.030, 0.034, 0.032, 0.038, 0.044, 0.054, 0.068, 0.105]
AMP_ROLL = [0.0, 0.006, 0.010, 0.014, 0.014, 0.014, 0.014, 0.016, 0.018, 0.024]

for step in range(91):  # 91 keyframes at 2-frame spacing -> t = 0.00 .. 6.00s
    frame = step * 2
    t = frame / 30.0
    for j in range(1, 10):
        pb = arm_obj.pose.bones[bone_names[j]]
        pb.rotation_mode = 'QUATERNION'
        phase = TAU * (t / 6.0) - (j - 1) * 0.56
        # Vertical undulation + gentle harmonic nuance + lateral swim + subtle roll
        vert = AMP_VERT[j] * math.sin(phase)
        lat = AMP_LAT[j] * math.cos(phase + 0.24)
        roll = AMP_ROLL[j] * math.sin(phase - 0.35)
        pb.rotation_quaternion = Euler((roll, vert, lat), 'XYZ').to_quaternion()
        pb.keyframe_insert(data_path='rotation_quaternion', frame=frame)
bpy.ops.object.mode_set(mode='OBJECT')

# Ensure linear interpolation on animation F-curves for exact 15 Hz sampling
if action.fcurves if hasattr(action, 'fcurves') else False:
    for fc in action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'

OUT_BLEND.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND), compress=True)

props = {p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties}
req = {
    'filepath': str(OUT_GLB),
    'export_format': 'GLB',
    'export_animations': True,
    'export_skins': True,
    'export_normals': True,
    'export_apply': False,
    'export_cameras': False,
    'export_lights': False,
}
bpy.ops.export_scene.gltf(**{k: v for k, v in req.items() if k in props})

print(json.dumps({
    'status': 'OK',
    'blender': bpy.app.version_string,
    'vertices': len(dragon_obj.data.vertices),
    'polygons': len(dragon_obj.data.polygons),
    'out_blend': str(OUT_BLEND),
    'out_glb': str(OUT_GLB),
    'glb_bytes': OUT_GLB.stat().st_size,
}, indent=2))
