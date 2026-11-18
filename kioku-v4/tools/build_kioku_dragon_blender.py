#!/usr/bin/env python3
"""KIOKU River Guardian — Native Blender 5.3 Modeling, Curve & Sculpt Pipeline.

Builds in Blender's native Z-up coordinate system:
  X = tail (-5.20) to snout (+3.30)
  Y = left (-Y) / right (+Y)
  Z = vertical height (UP)
When exported via Blender's glTF 2.0 exporter (Y-up), Blender automatically
maps (X, Y, Z)_blender -> (X, Z, -Y)_gltf for WebGL1 rendering.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector, Euler

ROOT = Path(__file__).resolve().parents[1]
OUT_GLB = ROOT / 'assets' / 'models' / 'kioku-river-guardian-v6-longform.glb'
OUT_BLEND = ROOT / 'assets' / 'models' / 'kioku-river-guardian-production.blend'

PI = math.pi
TAU = 2.0 * PI

# ---------------------------------------------------------------------------
# 0. Spine & Anatomical Proportions (Blender Z-up: X=length, Y=side, Z=UP)
# ---------------------------------------------------------------------------
SPINE_X = [-5.20, -4.55, -3.85, -3.10, -2.30, -1.50, -0.70, +0.08, +0.55, +0.98, +1.42, +1.82, +2.10]
SPINE_Z = [-0.46, -0.22, +0.34, +0.92, +1.14, +0.76, -0.02, -0.60, -0.44, +0.32, +0.84, +0.76, +0.66]
SPINE_Y = [-0.02, -0.04, -0.03, +0.00, +0.04, +0.04, +0.01, -0.03, -0.04, -0.02, +0.00, +0.01, +0.00]
SPINE_RZ = [0.028, 0.062, 0.125, 0.190, 0.238, 0.255, 0.262, 0.268, 0.260, 0.245, 0.235, 0.245, 0.252]
SPINE_RY = [0.026, 0.058, 0.118, 0.178, 0.224, 0.240, 0.246, 0.250, 0.242, 0.230, 0.222, 0.235, 0.248]

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
    return 0.5 * ((2.0 * p1) + (-p0 + p2) * t + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t * t + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t * t * t)


def spine_at(x: float):
    p = Vector((x, catmull_1d(SPINE_X, SPINE_Y, x), catmull_1d(SPINE_X, SPINE_Z, x)))
    return p, catmull_1d(SPINE_X, SPINE_RZ, x), catmull_1d(SPINE_X, SPINE_RY, x)


def spine_frame(x: float):
    dx = 0.02
    p0, _, _ = spine_at(max(SPINE_X[0], x - dx))
    p1, _, _ = spine_at(min(SPINE_X[-1], x + dx))
    tan = (p1 - p0).normalized()
    # In Blender Z-up, world Y is side, so up = tan x (-Y) or (+Y) x tan
    up = Vector((0.0, 1.0, 0.0)).cross(tan)
    if up.length < 1e-5:
        up = Vector((0.0, 0.0, 1.0))
    else:
        up.normalize()
    if up.z < 0:
        up = -up
    side = tan.cross(up).normalized()
    return tan, up, side


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
    ('KIOKU · river blue',     (0.019, 0.078, 0.198, 1.0), 0.04, 0.52),  # 0: Body cobalt-blue
    ('KIOKU · deep outline',   (0.004, 0.014, 0.054, 1.0), 0.02, 0.62),  # 1: Deep midnight-navy
    ('KIOKU · mist highlight', (0.578, 0.716, 0.791, 1.0), 0.02, 0.42),  # 2: Pale ice-blue belly/jaw
    ('KIOKU · muted teal',     (0.138, 0.342, 0.434, 1.0), 0.03, 0.48),  # 3: Glacier-teal accents
    ('KIOKU · horn bronze',    (0.012, 0.034, 0.112, 1.0), 0.05, 0.46),  # 4: Slate-navy horn/claws
    ('KIOKU · eye accent',     (0.855, 0.922, 0.956, 1.0), 0.01, 0.25),  # 5: Crisp white-ice sclera
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


def make_curve_mesh(name: str, pts, radii, mat_idx: int, bevel_res: int = 3, flatten_y: float = 1.0):
    cu = bpy.data.curves.new(name + '_curve', 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 10
    cu.bevel_depth = 1.0
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = True
    sp = cu.splines.new('NURBS')
    sp.points.add(len(pts) - 1)
    for i, (pt, rad) in enumerate(zip(pts, radii)):
        sp.points[i].co = (pt[0], pt[1], pt[2], 1.0)
        sp.points[i].radius = rad
    sp.use_endpoint_u = True
    sp.order_u = min(4, len(pts))
    obj = bpy.data.objects.new(name, cu)
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj = bpy.context.active_object
    obj.select_set(False)
    if flatten_y != 1.0:
        # Flatten thickness along Y toward the object's median Y so mane locks read as sculpted blades, not round cones
        ys = [v.co.y for v in obj.data.vertices]
        if ys:
            y_mid = sum(ys) / len(ys)
            for v in obj.data.vertices:
                v.co.y = y_mid + (v.co.y - y_mid) * flatten_y
    for m in materials:
        obj.data.materials.append(m)
    for p in obj.data.polygons:
        p.material_index = mat_idx
        p.use_smooth = True
    return obj


# ---------------------------------------------------------------------------
# 2. Build Serpentine Body in BMesh (Z-up)
# ---------------------------------------------------------------------------
def build_body():
    bm = bmesh.new()
    rings = 180
    cols = 28
    xs = [SPINE_X[0] + (SPINE_X[-1] - SPINE_X[0]) * i / (rings - 1) for i in range(rings)]
    grid = []
    for i, x in enumerate(xs):
        c, rz, ry = spine_at(x)
        _, up, side = spine_frame(x)
        ring = []
        for k in range(cols):
            ang = TAU * k / cols  # 0 = top (+up), PI = bottom (-up)
            ca, sa = math.cos(ang), math.sin(ang)
            ang_s = ang if ang <= PI else ang - TAU
            rmod = 1.0
            if abs(ang_s) < 0.45:
                rmod += 0.08 * math.exp(-((ang_s / 0.22) ** 2))
            if abs(ang - PI) < 0.92:
                # Subtle physical scute indentation on belly (no harsh zebra stripes)
                seg_wave = math.cos((x + 5.2) * (TAU / 0.36))
                rmod *= 0.96 - 0.028 * max(0.0, seg_wave) ** 6
            pt = c + up * (ca * rz * rmod) + side * (sa * ry * rmod)
            ring.append(bm.verts.new(pt))
        grid.append(ring)

    bm.verts.ensure_lookup_table()
    for i in range(rings - 1):
        x_mid = 0.5 * (xs[i] + xs[i + 1])
        # Very thin scute seam (only when cos > 0.96)
        seg_groove = math.cos((x_mid + 5.2) * (TAU / 0.36)) > 0.955
        for k in range(cols):
            kn = (k + 1) % cols
            f = bm.faces.new((grid[i][k], grid[i + 1][k], grid[i + 1][kn], grid[i][kn]))
            ang_mid = TAU * ((k + 0.5) / cols)
            if ang_mid > PI:
                ang_mid -= TAU
            if abs(ang_mid) < 0.72:
                f.material_index = 1
            elif abs(ang_mid) > 2.18:
                f.material_index = 1 if seg_groove else 2
            else:
                f.material_index = 0

    tail_tip = bm.verts.new(spine_at(SPINE_X[0])[0] + Vector((-0.05, 0.0, -0.01)))
    for k in range(cols):
        bm.faces.new((grid[0][(k + 1) % cols], grid[0][k], tail_tip)).material_index = 1

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('KIOKU_Body')
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new('KIOKU_Body', me)
    scene.collection.objects.link(obj)
    for m in materials:
        obj.data.materials.append(m)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


# ---------------------------------------------------------------------------
# 3. Build Sculpted East Asian Dragon Head (Z-up, Subsurf + Deep-Set Eyes)
# ---------------------------------------------------------------------------
def build_head_and_face():
    objs = []
    bm = bmesh.new()
    hx = [1.88, 2.04, 2.20, 2.36, 2.50, 2.64, 2.78, 2.92, 3.04, 3.14, 3.22, 3.28]
    hz_top = [0.90, 0.96, 1.02, 1.04, 1.00, 0.94, 0.91, 0.92, 0.94, 0.96, 0.94, 0.88]
    hz_bot = [0.40, 0.36, 0.34, 0.35, 0.39, 0.45, 0.52, 0.59, 0.65, 0.70, 0.73, 0.76]
    hry = [0.25, 0.30, 0.34, 0.35, 0.31, 0.26, 0.22, 0.19, 0.17, 0.15, 0.12, 0.06]
    cols = 24
    grid = []
    for i, x in enumerate(hx):
        cz = 0.5 * (hz_top[i] + hz_bot[i])
        rz = 0.5 * (hz_top[i] - hz_bot[i])
        ry = hry[i]
        ring = []
        for k in range(cols):
            ang = TAU * k / cols
            ca, sa = math.cos(ang), math.sin(ang)
            ang_s = ang if ang <= PI else ang - TAU
            z_off = ca * rz
            y_off = sa * ry
            # Bold brow ridge overhang
            if 2.34 <= x <= 2.84 and 0.50 <= abs(ang_s) <= 1.08:
                z_off += 0.048 * math.exp(-(((x - 2.58) / 0.18) ** 2))
                y_off += math.copysign(0.036, sa)
            # Orbital socket recess directly under brow
            if 2.42 <= x <= 2.82 and 1.08 < abs(ang_s) <= 1.65:
                y_off *= 0.84
            # Cheekbone flare
            if 2.30 <= x <= 2.82 and 1.65 < abs(ang_s) <= 2.25:
                y_off *= 1.14
            # Flared nostril boss
            if 3.06 <= x <= 3.25 and 0.40 <= abs(ang_s) <= 1.10:
                z_off += 0.025
                y_off += math.copysign(0.022, sa)
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
            # Smooth anatomical material zones (no abrupt square step on forehead/cheek):
            # - Top dorsal cranium & nasal bridge (|ang| < 0.72) -> Mat 1 (deep navy)
            # - Pale under-jaw / chin (|ang| > 2.15) -> Mat 2 (pale ice-blue)
            # - River-blue cheeks & muzzle -> Mat 0 (river blue)
            if abs(ang_m) > 2.15:
                f.material_index = 2
            elif abs(ang_m) < 0.72:
                f.material_index = 1
            else:
                f.material_index = 0

    tip_v = bm.verts.new((3.31, 0.0, 0.83))
    for k in range(cols):
        bm.faces.new((grid[-1][k], tip_v, grid[-1][(k + 1) % cols])).material_index = 0

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me_h = bpy.data.meshes.new('KIOKU_Head')
    bm.to_mesh(me_h)
    bm.free()
    head_obj = bpy.data.objects.new('KIOKU_Head', me_h)
    scene.collection.objects.link(head_obj)
    for m in materials:
        head_obj.data.materials.append(m)
    for p in head_obj.data.polygons:
        p.use_smooth = True
    sub = head_obj.modifiers.new('Subsurf', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1
    bpy.context.view_layer.objects.active = head_obj
    bpy.ops.object.modifier_apply(modifier=sub.name)
    objs.append(head_obj)

    # Smooth Muted-Teal Snout Bridge & Cheek Sweep + Bold Almond Eyes + Brow + Mouth + Beard
    objs.append(make_curve_mesh(
        'Snout_Bridge_Teal',
        [(2.68, 0.0, 0.875), (2.86, 0.0, 0.865), (3.06, 0.0, 0.895), (3.20, 0.0, 0.880)],
        [0.036, 0.082, 0.078, 0.028],
        mat_idx=3, bevel_res=3
    ))
    for s in (-1.0, 1.0):
        # Smooth sculpted muted-teal cheek/jaw sweep (tapered at both ends)
        objs.append(make_curve_mesh(
            f'Cheek_Sweep_{s:+.0f}',
            [(2.36, s * 0.27, 0.50), (2.58, s * 0.27, 0.56), (2.82, s * 0.21, 0.62), (3.06, s * 0.15, 0.70)],
            [0.025, 0.068, 0.056, 0.018],
            mat_idx=3, bevel_res=3, flatten_y=0.45
        ))
        # Bold Deep-Navy Brow Ridge sweeping over the eye
        objs.append(make_curve_mesh(
            f'Brow_Ridge_{s:+.0f}',
            [(2.36, s * 0.27, 0.68), (2.54, s * 0.27, 0.78), (2.74, s * 0.24, 0.78), (2.90, s * 0.19, 0.73)],
            [0.024, 0.046, 0.042, 0.016],
            mat_idx=1, bevel_res=3, flatten_y=0.55
        ))
        # Almond Sclera (Mat 5) tucked cleanly under the dark navy brow
        objs.append(make_curve_mesh(
            f'Eye_Sclera_{s:+.0f}',
            [(2.46, s * 0.268, 0.640), (2.58, s * 0.272, 0.675), (2.71, s * 0.248, 0.702), (2.82, s * 0.214, 0.716)],
            [0.010, 0.046, 0.048, 0.008],
            mat_idx=5, bevel_res=3, flatten_y=0.45
        ))
        # Dark Navy Pupil/Iris (Mat 1) inside the eye
        objs.append(make_curve_mesh(
            f'Eye_Pupil_{s:+.0f}',
            [(2.62, s * 0.282, 0.678), (2.69, s * 0.272, 0.692), (2.75, s * 0.252, 0.704)],
            [0.024, 0.036, 0.018],
            mat_idx=1, bevel_res=3, flatten_y=0.45
        ))
        # Crisp Dark-Navy Mouth Cleft (Mat 1)
        objs.append(make_curve_mesh(
            f'Mouth_Line_{s:+.0f}',
            [(2.56, s * 0.265, 0.50), (2.82, s * 0.205, 0.59), (3.06, s * 0.155, 0.69), (3.22, s * 0.105, 0.76)],
            [0.012, 0.011, 0.009, 0.004],
            mat_idx=1, bevel_res=2
        ))
        # Nostril Hollow (Mat 1)
        objs.append(make_curve_mesh(
            f'Nostril_{s:+.0f}',
            [(3.14, s * 0.115, 0.855), (3.20, s * 0.102, 0.865)],
            [0.014, 0.010],
            mat_idx=1, bevel_res=2
        ))

    # 3 Sleek Chin Beard Tufts (Mat 1)
    for i, (tx, tz, tl) in enumerate([(2.46, 0.37, 0.11), (2.30, 0.35, 0.13), (2.14, 0.37, 0.11)]):
        objs.append(make_curve_mesh(
            f'Chin_Tuft_{i}',
            [(tx + 0.04, 0.0, tz + 0.03), (tx - 0.04, 0.0, tz - tl * 0.6), (tx - 0.13, 0.0, tz - tl)],
            [0.032, 0.022, 0.003],
            mat_idx=1, bevel_res=2
        ))

    return objs


# ---------------------------------------------------------------------------
# 4. Horns, Swept Flame Mane & Single Pair of Whiskers (Z-up Curves)
# ---------------------------------------------------------------------------
def build_horns_mane_whiskers():
    objs = []
    for s in (-1.0, 1.0):
        # Main Deep-Navy Stag Antler: organic S-curved sweep backward-upward with a single curved Y-fork
        objs.append(make_curve_mesh(
            f'Antler_Main_{s:+.0f}',
            [(2.34, s * 0.12, 0.94), (2.16, s * 0.14, 1.06), (1.88, s * 0.17, 1.22), (1.58, s * 0.19, 1.34), (1.36, s * 0.20, 1.44)],
            [0.068, 0.052, 0.036, 0.020, 0.004],
            mat_idx=1, bevel_res=3
        ))
        objs.append(make_curve_mesh(
            f'Antler_Fork_{s:+.0f}',
            [(2.04, s * 0.15, 1.12), (2.06, s * 0.17, 1.26), (2.14, s * 0.18, 1.40), (2.26, s * 0.19, 1.50)],
            [0.038, 0.028, 0.018, 0.004],
            mat_idx=1, bevel_res=3
        ))

        # Rear/Outer Muted-Teal Secondary Horn (swept gracefully back)
        objs.append(make_curve_mesh(
            f'Horn_Teal_Main_{s:+.0f}',
            [(2.14, s * 0.17, 0.90), (1.86, s * 0.21, 1.02), (1.56, s * 0.24, 1.14), (1.30, s * 0.26, 1.22)],
            [0.058, 0.042, 0.024, 0.004],
            mat_idx=3, bevel_res=3
        ))
        objs.append(make_curve_mesh(
            f'Horn_Teal_Fork_{s:+.0f}',
            [(1.78, s * 0.22, 1.05), (1.62, s * 0.24, 1.18), (1.48, s * 0.25, 1.28)],
            [0.030, 0.018, 0.004],
            mat_idx=3, bevel_res=2
        ))

        # Layered Swept-Back Flame Mane Locks (flattened blade cross-sections hugging the neck!)
        mane_specs = [
            ([(2.28, s * 0.14, 0.88), (1.96, s * 0.20, 0.95), (1.62, s * 0.23, 0.96), (1.34, s * 0.24, 1.05)], [0.068, 0.062, 0.036, 0.004], 1),
            ([(2.32, s * 0.18, 0.76), (1.92, s * 0.24, 0.80), (1.52, s * 0.27, 0.74), (1.18, s * 0.28, 0.82)], [0.084, 0.076, 0.042, 0.004], 1),
            ([(2.32, s * 0.21, 0.64), (1.94, s * 0.26, 0.62), (1.58, s * 0.29, 0.56), (1.28, s * 0.30, 0.60)], [0.052, 0.046, 0.024, 0.003], 3),
            ([(2.30, s * 0.20, 0.54), (1.90, s * 0.25, 0.50), (1.50, s * 0.28, 0.42), (1.18, s * 0.29, 0.46)], [0.078, 0.070, 0.036, 0.004], 1),
            ([(2.24, s * 0.17, 0.42), (1.92, s * 0.22, 0.36), (1.60, s * 0.25, 0.28), (1.34, s * 0.26, 0.32)], [0.064, 0.054, 0.028, 0.004], 1),
        ]
        for idx_m, (pts, rads, mat_i) in enumerate(mane_specs):
            objs.append(make_curve_mesh(f'Mane_{s:+.0f}_{idx_m}', pts, rads, mat_idx=mat_i, bevel_res=3, flatten_y=0.38))

    # Single Pair of Calligraphy S-Curved Whiskers (Mat 3)
    objs.append(make_curve_mesh(
        'Whisker_Up',
        [(3.12, +0.11, 0.84), (3.36, +0.17, 0.94), (3.60, +0.23, 1.14), (3.76, +0.25, 1.38), (3.66, +0.21, 1.54)],
        [0.013, 0.010, 0.007, 0.005, 0.002],
        mat_idx=3, bevel_res=2
    ))
    objs.append(make_curve_mesh(
        'Whisker_Down',
        [(3.10, -0.11, 0.78), (3.36, -0.17, 0.68), (3.62, -0.23, 0.64), (3.88, -0.25, 0.66), (3.98, -0.21, 0.50)],
        [0.013, 0.010, 0.007, 0.005, 0.002],
        mat_idx=3, bevel_res=2
    ))
    return objs


# ---------------------------------------------------------------------------
# 5. Dorsal Flame Tufts, 2 Pairs of Articulated Dragon Limbs & Tail Fin
# ---------------------------------------------------------------------------
def build_crest_limbs_tail():
    objs = []
    crest_specs = [
        (1.36, 0.38, 0.062),
        (1.06, 0.44, 0.068),
        (-1.90, 0.34, 0.056),
        (-2.35, 0.36, 0.058),
        (-2.80, 0.32, 0.052),
    ]
    for idx_c, (xc, length_c, rad_c) in enumerate(crest_specs):
        p, rz, _ = spine_at(xc)
        tan, up, _ = spine_frame(xc)
        pts = [
            p + up * (rz * 0.72) + tan * 0.14,
            p + up * (rz + 0.09) - tan * (length_c * 0.35),
            p + up * (rz + 0.12) - tan * length_c,
        ]
        objs.append(make_curve_mesh(f'Dorsal_Tuft_{idx_c}', pts, [rad_c, rad_c * 0.72, 0.004], mat_idx=1, bevel_res=3))

    limb_specs = [
        ('Upper_Limb', 0.92, (0.0, 1.0, 0.10), (0.28, 0.12, 0.04), (0.52, 0.05, -0.08), (0.64, 0.02, -0.14), 0.92),
        ('Lower_Limb', 0.10, (0.0, 1.0, -0.55), (-0.12, 0.12, -0.26), (0.04, 0.05, -0.48), (0.16, 0.02, -0.54), 1.00),
    ]
    for lname, x_att, sdir, eoff, woff, poff, sc in limb_specs:
        cp, rz, ry = spine_at(x_att)
        for s in (-1.0, 1.0):
            sh = cp + Vector((0.0, s * ry * 0.80, sdir[2] * rz))
            el = sh + Vector((eoff[0] * sc, s * eoff[1] * sc, eoff[2] * sc))
            wr = sh + Vector((woff[0] * sc, s * woff[1] * sc, woff[2] * sc))
            pa = sh + Vector((poff[0] * sc, s * poff[1] * sc, poff[2] * sc))
            objs.append(make_curve_mesh(
                f'{lname}_{s:+.0f}', [sh, el, wr, pa],
                [0.085 * sc, 0.062 * sc, 0.044 * sc, 0.036 * sc],
                mat_idx=0, bevel_res=3
            ))
            objs.append(make_curve_mesh(
                f'{lname}_Plume_{s:+.0f}',
                [el, el + Vector((-0.18 * sc, s * 0.06 * sc, -0.02 * sc)), el + Vector((-0.34 * sc, s * 0.10 * sc, 0.04 * sc))],
                [0.040 * sc, 0.024 * sc, 0.003],
                mat_idx=1, bevel_res=2
            ))
            for ci, (cz, cy) in enumerate([(0.04, -0.05), (0.01, -0.02), (-0.02, 0.02), (-0.05, 0.05)]):
                c0 = pa + Vector((0.0, cy * sc * 0.5, cz * 0.5))
                c1 = c0 + Vector((0.09 * sc, cy * sc * 1.2, cz - 0.015))
                c2 = c1 + Vector((0.07 * sc, cy * sc * 1.3, cz - 0.05))
                objs.append(make_curve_mesh(f'{lname}_Claw_{s:+.0f}_{ci}', [c0, c1, c2], [0.024 * sc, 0.016 * sc, 0.004], mat_idx=4, bevel_res=2))

    # Swept Multi-Layered Flame Tail Fin
    t_root, _, _ = spine_at(SPINE_X[0])
    objs.append(make_curve_mesh(
        'Tail_Fin_Main',
        [t_root + Vector((0.12, 0.0, 0.01)), t_root + Vector((-0.22, 0.0, -0.04)), t_root + Vector((-0.56, 0.0, 0.04)), t_root + Vector((-0.86, 0.0, 0.22))],
        [0.032, 0.054, 0.038, 0.003], mat_idx=1, bevel_res=3
    ))
    objs.append(make_curve_mesh(
        'Tail_Fin_Mid',
        [t_root + Vector((0.06, 0.0, -0.01)), t_root + Vector((-0.28, 0.02, -0.06)), t_root + Vector((-0.62, 0.03, -0.01))],
        [0.024, 0.036, 0.003], mat_idx=0, bevel_res=2
    ))
    objs.append(make_curve_mesh(
        'Tail_Fin_Teal',
        [t_root + Vector((0.04, -0.01, 0.02)), t_root + Vector((-0.30, -0.02, 0.04)), t_root + Vector((-0.66, -0.02, 0.16))],
        [0.020, 0.028, 0.003], mat_idx=3, bevel_res=2
    ))
    return objs


# ---------------------------------------------------------------------------
# 6. Join Mesh Parts, Bind 10-Bone Rig & Export Clean GLB + .blend
# ---------------------------------------------------------------------------
all_parts = [build_body()] + build_head_and_face() + build_horns_mane_whiskers() + build_crest_limbs_tail()
bpy.ops.object.select_all(action='DESELECT')
for o in all_parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = all_parts[0]
bpy.ops.object.join()
dragon_obj = bpy.context.active_object
dragon_obj.name = 'KIOKU_River_Guardian_Mesh'

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
    tail_x = BONE_WORLD_X[i] - 0.45 if i == 9 else BONE_WORLD_X[i + 1]
    tail_p, _, _ = spine_at(tail_x)
    eb.head = head_p
    eb.tail = tail_p
    if i > 0:
        eb.parent = ebones[i - 1]
        eb.use_connect = True
    eb.use_deform = True
    ebones.append(eb)
bpy.ops.object.mode_set(mode='OBJECT')

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

arm_obj.animation_data_create()
action = bpy.data.actions.new('River Guardian V6 Longform — Sculpted 6s Swim')
arm_obj.animation_data.action = action
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
for frame in range(0, 181, 10):
    t = frame / 30.0
    for j in range(1, 10):
        pb = arm_obj.pose.bones[bone_names[j]]
        pb.rotation_mode = 'QUATERNION'
        amp = [0.0, 0.024, 0.040, 0.056, 0.070, 0.084, 0.096, 0.108, 0.118, 0.126][j]
        phase = TAU * (t / 6.0) - (j - 1) * 0.42
        # In Blender Z-up: Z is yaw (side-to-side swim), Y is vertical pitch wave, X is roll twist
        eul = Euler((0.15 * amp * math.sin(phase - 0.35), amp * math.sin(phase), 0.55 * amp * math.cos(phase + 0.25)), 'XYZ')
        pb.rotation_quaternion = eul.to_quaternion()
        pb.keyframe_insert(data_path='rotation_quaternion', frame=frame)
bpy.ops.object.mode_set(mode='OBJECT')

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
