import bpy
import bmesh
import os
import pickle
import hashlib
import numpy as np

MASTER_BLEND = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/round-35/KIOKU-Dragon-Rebuild.blend"
EXPECTED_SHA = "b766630dabd090fd9db09becb729a5d2bc269c60bd1652334e86cee0ccfecea7"
TEX_DIR = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/web-round35/baked_textures"
MESH_STAGE_BLEND = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/web-round35/KIOKU-Dragon-Web-MeshStage.blend"
POSES_PKL = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/web-round35/evaluated_poses.pkl"

h = hashlib.sha256()
with open(MASTER_BLEND, "rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
        h.update(chunk)
assert h.hexdigest() == EXPECTED_SHA, "Master SHA-256 mismatch!"

bpy.ops.wm.open_mainfile(filepath=MASTER_BLEND)
sc = bpy.data.scenes["Scene"]
bpy.context.window.scene = sc
for other_sc in list(bpy.data.scenes):
    if other_sc != sc:
        bpy.data.scenes.remove(other_sc)

arm = bpy.data.objects["KIOKU_HeadRig"]
def_bone_names = [b.name for b in arm.data.bones if b.use_deform]
deps = bpy.context.evaluated_depsgraph_get()

# 1. Sample exact evaluated world-space pose matrices for all 74 DEF_* bones
world_poses = {}
for f in [1] + list(range(380, 458)):
    sc.frame_set(f)
    ev_arm = arm.evaluated_get(deps)
    mw = ev_arm.matrix_world
    world_poses[f] = {bn: [list(row) for row in (mw @ ev_arm.pose.bones[bn].matrix)] for bn in def_bone_names}

with open(POSES_PKL, "wb") as fp:
    pickle.dump(world_poses, fp)

sc.frame_set(1)
deps = bpy.context.evaluated_depsgraph_get()

# 2. Evaluate KIOKU_TailTuft_Blockout GN mesh at rest frame 1 & transfer DEF_Tail weights
tuft = bpy.data.objects["KIOKU_TailTuft_Blockout"]
ev_tuft = tuft.evaluated_get(deps)
new_tuft_me = bpy.data.meshes.new_from_object(ev_tuft)
old_tuft_me = tuft.data
tuft.modifiers.clear()
tuft.data = new_tuft_me
bpy.data.meshes.remove(old_tuft_me)

body = bpy.data.objects["KIOKU_Body_Blockout"]
bpy.ops.object.select_all(action="DESELECT")
tuft.select_set(True)
bpy.context.view_layer.objects.active = tuft
dt = tuft.modifiers.new("TailWeightTransfer", "DATA_TRANSFER")
dt.object = body
dt.use_vert_data = True
dt.data_types_verts = {"VGROUP_WEIGHTS"}
dt.vert_mapping = "POLYINTERP_NEAREST"
bpy.ops.object.datalayout_transfer(modifier=dt.name)
bpy.ops.object.modifier_apply(modifier=dt.name)

# 3. Convert rigid bone/object-parented parts to KIOKU_HeadRig vertex-group skinning
def bind_rigid(obj_name, bone_name):
    obj = bpy.data.objects[obj_name]
    mw = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = mw
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.vertex_groups.clear()
    vg = obj.vertex_groups.new(name=bone_name)
    vg.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    obj.modifiers.clear()

for nm in ["KIOKU_LowerJaw", "KIOKU_Teeth_Lower", "KIOKU_Gums_Lower", "KIOKU_Tongue", "KIOKU_HeadGroom_ChinBeard"]:
    bind_rigid(nm, "DEF_Jaw")
for nm in ["KIOKU_Horns", "KIOKU_Teeth_Upper", "KIOKU_Gums_Upper", "KIOKU_EyeWetRim"]:
    bind_rigid(nm, "DEF_Head")

# 4. Encode Dual-Realm Groom attributes (Water -> COLOR_0, Coral RG -> UVMap, Coral B + groom_u -> UVCoralBU)
groom_names = [
    "KIOKU_HeadGroom_Brows",
    "KIOKU_HeadGroom_CheekJaw",
    "KIOKU_HeadGroom_ChinBeard",
    "KIOKU_HeadGroom_Mane",
    "KIOKU_BackTailGroom_Crest",
]
for gname in groom_names:
    me = bpy.data.objects[gname].data
    nv = len(me.vertices)
    wc = np.zeros(nv * 4, dtype=np.float32)
    cc = np.zeros(nv * 4, dtype=np.float32)
    gu = np.zeros(nv, dtype=np.float32)
    gid = np.zeros(nv, dtype=np.float32)
    gund = np.zeros(nv, dtype=np.float32)
    me.attributes["groom_water_col"].data.foreach_get("color", wc)
    me.attributes["groom_coral_col"].data.foreach_get("color", cc)
    me.attributes["groom_u"].data.foreach_get("value", gu)
    me.attributes["groom_id"].data.foreach_get("value", gid)
    if me.attributes.get("groom_under"):
        me.attributes["groom_under"].data.foreach_get("value", gund)
    wc, cc = wc.reshape(-1, 4), cc.reshape(-1, 4)

    pv = np.zeros(len(me.loops), dtype=np.int32)
    me.loops.foreach_get("vertex_index", pv)
    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])
    uv0 = me.uv_layers.new(name="UVMap")
    uv1 = me.uv_layers.new(name="UVCoralBU")
    uv0.data.foreach_set("uv", np.column_stack([np.clip(cc[pv, 0], 0, 1), 1.0 - np.clip(cc[pv, 1], 0, 1)]).astype(np.float32).ravel())
    uv1.data.foreach_set("uv", np.column_stack([np.clip(cc[pv, 2], 0, 1), 1.0 - np.clip(gu[pv], 0, 1)]).astype(np.float32).ravel())

    ca = me.color_attributes.new(name="Color", type="BYTE_COLOR", domain="CORNER")
    lw = np.clip(wc[pv], 0, 1).astype(np.float32)
    lw[:, 3] = 1.0
    ca.data.foreach_set("color", lw.ravel())
    me.color_attributes.active_color = ca
    me.color_attributes.render_color_index = 0

    drop_v = (gund > 0.5) & ((np.round(gid * 997).astype(np.int64) % 3) != 0)
    if np.any(drop_v):
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[i] for i in np.where(drop_v)[0]], context="VERTS")
        bm.to_mesh(me)
        bm.free()

def join_objs(names, new_name):
    bpy.ops.object.select_all(action="DESELECT")
    for nm in names:
        bpy.data.objects[nm].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[names[0]]
    bpy.ops.object.join()
    o = bpy.context.active_object
    o.name = new_name
    return o

groom_web = join_objs(groom_names, "KIOKU_Groom_Web")
teeth_web = join_objs(["KIOKU_Teeth_Upper", "KIOKU_Teeth_Lower"], "KIOKU_Teeth_Web")
oral_web = join_objs(["KIOKU_Gums_Upper", "KIOKU_Gums_Lower", "KIOKU_Tongue"], "KIOKU_Oral_Web")

# 5. Split Eyes into Inner + Cornea, scale Body UVs, and apply smart decimation
eyes_in = bpy.data.objects["KIOKU_Eyes"]
eyes_co = eyes_in.copy()
eyes_co.data = eyes_in.data.copy()
sc.collection.objects.link(eyes_co)
eyes_in.name, eyes_co.name = "KIOKU_Eyes_Inner", "KIOKU_Eyes_Cornea"
for tobj, is_co in [(eyes_in, False), (eyes_co, True)]:
    bm = bmesh.new()
    bm.from_mesh(tobj.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if (f.material_index == 3) != is_co], context="FACES")
    bm.to_mesh(tobj.data)
    bm.free()

uv_b = np.zeros(len(body.data.loops) * 2, dtype=np.float32)
body.data.uv_layers["UVMap"].data.foreach_get("uv", uv_b)
uv_b = uv_b.reshape(-1, 2)
uv_b[:, 0] *= 0.2
body.data.uv_layers["UVMap"].data.foreach_set("uv", uv_b.ravel())
body.modifiers.clear()

b_co = np.zeros(len(body.data.vertices) * 3, dtype=np.float32)
body.data.vertices.foreach_get("co", b_co)
prot_vg = body.vertex_groups.new(name="_WebProtect")
for idx, (vx, vy, vz) in enumerate(b_co.reshape(-1, 3)):
    if vx > 4.55:
        prot_vg.add([idx], 1.0, "REPLACE")
    elif vx > 4.05:
        prot_vg.add([idx], 0.55, "REPLACE")
    elif vz < 0.14:
        prot_vg.add([idx], 0.65, "REPLACE")

def decimate(obj, ratio, vg=None):
    if obj.data.shape_keys:
        obj.shape_key_clear()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    d = obj.modifiers.new("WebDec", "DECIMATE")
    d.ratio = ratio
    if vg:
        d.vertex_group, d.invert_vertex_group, d.vertex_group_factor = vg, True, 0.85
    bpy.ops.object.modifier_apply(modifier=d.name)
    if vg and obj.vertex_groups.get(vg):
        obj.vertex_groups.remove(obj.vertex_groups[vg])

decimate(body, 0.20, "_WebProtect")
decimate(groom_web, 0.36)
decimate(tuft, 0.18)
decimate(bpy.data.objects["KIOKU_Horns"], 0.20)
decimate(bpy.data.objects["KIOKU_VentralPlates"], 0.42)
decimate(bpy.data.objects["KIOKU_Claws"], 0.42)
decimate(bpy.data.objects["KIOKU_Whiskers"], 0.52)
decimate(teeth_web, 0.22)
decimate(oral_web, 0.05)
decimate(bpy.data.objects["KIOKU_EyeWetRim"], 0.35)
join_objs(["KIOKU_Eyes_Cornea", "KIOKU_EyeWetRim"], "KIOKU_Eyes_Cornea")

for fx_name, ua, va in [("KIOKU_Sky_ManeFlameRibbons", "flame_u", "flame_v"), ("KIOKU_Sky_AuraHalo", "aura_env", None)]:
    fx_obj = bpy.data.objects[fx_name]
    if fx_obj.name not in sc.collection.objects:
        sc.collection.objects.link(fx_obj)
    if fx_obj.data.shape_keys:
        fx_obj.shape_key_clear()
    fme = fx_obj.data
    pv = np.zeros(len(fme.loops), dtype=np.int32)
    fme.loops.foreach_get("vertex_index", pv)
    u_a = np.zeros(len(fme.vertices), dtype=np.float32)
    fme.attributes[ua].data.foreach_get("value", u_a)
    v_a = np.zeros(len(fme.vertices), dtype=np.float32)
    if va and fme.attributes.get(va):
        fme.attributes[va].data.foreach_get("value", v_a)
    fme.uv_layers.new(name="UVMap").data.foreach_set("uv", np.column_stack([u_a[pv], 1.0 - v_a[pv]]).astype(np.float32).ravel())

bpy.ops.wm.save_as_mainfile(filepath=MESH_STAGE_BLEND)
print("SAVED MESH STAGE:", MESH_STAGE_BLEND)
