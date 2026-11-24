import bpy
import os
import json
import pickle
import shutil
from mathutils import Matrix, Quaternion

EXPECTED_SHA = "b766630dabd090fd9db09becb729a5d2bc269c60bd1652334e86cee0ccfecea7"
MASTER_BLEND = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/round-35/KIOKU-Dragon-Rebuild.blend"
TEX_DIR = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/web-round35/baked_textures"
MESH_STAGE_BLEND = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/web-round35/KIOKU-Dragon-Web-MeshStage.blend"
DERIV_BLEND = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/web-round35/KIOKU-Dragon-Web-Derivative.blend"
POSES_PKL = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/web-round35/evaluated_poses.pkl"
WEB_MODELS_DIR = "/tmp/kioku-round35-web/kioku-v4/assets/models"
WEB_IMG_DIR = "/tmp/kioku-round35-web/kioku-v4/assets/img"
WEB_TEX_DIR = os.path.join(WEB_MODELS_DIR, "textures")
GLB_OUT = os.path.join(WEB_MODELS_DIR, "KIOKU-Dragon-Web.glb")
MANIFEST_OUT = os.path.join(WEB_MODELS_DIR, "kioku-dragon-web-manifest.json")

os.makedirs(WEB_TEX_DIR, exist_ok=True)
os.makedirs(WEB_IMG_DIR, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=MESH_STAGE_BLEND)
sc = bpy.context.scene
arm = bpy.data.objects["KIOKU_HeadRig"]

with open(POSES_PKL, "rb") as fp:
    raw_poses = pickle.load(fp)
world_poses = {f: {bn: Matrix(m) for bn, m in bd.items()} for f, bd in raw_poses.items()}

keep_meshes = [
    "KIOKU_Body_Blockout",
    "KIOKU_LowerJaw",
    "KIOKU_VentralPlates",
    "KIOKU_Horns",
    "KIOKU_Claws",
    "KIOKU_Whiskers",
    "KIOKU_Eyes_Inner",
    "KIOKU_Eyes_Cornea",
    "KIOKU_Teeth_Web",
    "KIOKU_Oral_Web",
    "KIOKU_Groom_Web",
    "KIOKU_TailTuft_Blockout",
    "KIOKU_Sky_ManeFlameRibbons",
    "KIOKU_Sky_AuraHalo",
]
for obj in list(bpy.data.objects):
    if obj != arm and obj.name not in keep_meshes:
        bpy.data.objects.remove(obj, do_unlink=True)

keep_uvs = {"UVMap", "UVCoralBU"}
for mname in keep_meshes:
    obj = bpy.data.objects[mname]
    me = obj.data
    for uvl in list(me.uv_layers):
        if uvl.name not in keep_uvs:
            me.uv_layers.remove(uvl)
    for attr in list(me.attributes):
        if attr.name not in ("position", "UVMap", "UVCoralBU", "Color", "material_index") and not attr.name.startswith("."):
            me.attributes.remove(attr)
    me.shade_smooth()
    mw = obj.matrix_world.copy()
    obj.parent = arm
    obj.matrix_parent_inverse = arm.matrix_world.inverted() @ mw
    obj.modifiers.clear()
    am = obj.modifiers.new("Armature", "ARMATURE")
    am.object = arm

def make_mat(name, base_tex=None, norm_tex=None, rough_tex=None, col=(1,1,1,1), rough=0.42, alpha=1.0, vcol=False):
    mat = bpy.data.materials.new(name=name)
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = col
    bsdf.inputs["Roughness"].default_value = rough
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.surface_render_method = "BLENDED"
    if vcol:
        vc = nt.nodes.new("ShaderNodeVertexColor")
        vc.layer_name = "Color"
        nt.links.new(vc.outputs["Color"], bsdf.inputs["Base Color"])
    if base_tex:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(os.path.join(TEX_DIR, base_tex))
        t.image.colorspace_settings.name = "sRGB"
        nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    if rough_tex:
        tr = nt.nodes.new("ShaderNodeTexImage")
        tr.image = bpy.data.images.load(os.path.join(TEX_DIR, rough_tex))
        tr.image.colorspace_settings.name = "Non-Color"
        nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])
    if norm_tex:
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = bpy.data.images.load(os.path.join(TEX_DIR, norm_tex))
        tn.image.colorspace_settings.name = "Non-Color"
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return mat

def assign(obj_name, mat):
    o = bpy.data.objects[obj_name]
    o.data.materials.clear()
    o.data.materials.append(mat)

assign("KIOKU_Body_Blockout", make_mat("MAT_Web_Skin", "skin_water_base.webp", "skin_normal.png", "skin_roughness.webp"))
assign("KIOKU_LowerJaw", make_mat("MAT_Web_Jaw", "jaw_water_base.webp", "jaw_normal.png", rough=0.38))
assign("KIOKU_VentralPlates", make_mat("MAT_Web_Ventral", "ventral_water_base.webp", "ventral_normal.png", rough=0.40))
assign("KIOKU_Horns", make_mat("MAT_Web_Horn", "horn_base.webp", "horn_normal.png", rough=0.34))
assign("KIOKU_Claws", make_mat("MAT_Web_Claw", "claw_water_base.webp", rough=0.26))
assign("KIOKU_Whiskers", make_mat("MAT_Web_Whisker", col=(0.88, 0.85, 0.78, 1.0), rough=0.28))
assign("KIOKU_Eyes_Inner", make_mat("MAT_Web_EyeInner", "eye_base.webp", "eye_normal.png", rough=0.10))
assign("KIOKU_Eyes_Cornea", make_mat("MAT_Web_EyeCornea", col=(0.95, 0.98, 1.0, 1.0), rough=0.02, alpha=0.14))
assign("KIOKU_Teeth_Web", make_mat("MAT_Web_Tooth", col=(0.86, 0.82, 0.73, 1.0), rough=0.16))
assign("KIOKU_Oral_Web", make_mat("MAT_Web_Oral", col=(0.20, 0.08, 0.08, 1.0), rough=0.28))
assign("KIOKU_Groom_Web", make_mat("MAT_Web_Groom", rough=0.46, vcol=True))
assign("KIOKU_TailTuft_Blockout", make_mat("MAT_Web_Tuft", "tuft_water_base.webp", rough=0.48))
assign("KIOKU_Sky_ManeFlameRibbons", make_mat("MAT_Web_FlameRibbon", col=(1.0, 0.36, 0.08, 1.0), rough=0.3, alpha=0.65))
assign("KIOKU_Sky_AuraHalo", make_mat("MAT_Web_AuraHalo", col=(1.0, 0.42, 0.12, 1.0), rough=0.5, alpha=0.25))

bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
if arm.animation_data:
    arm.animation_data_clear()
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"
    for c in list(pb.constraints):
        pb.constraints.remove(c)

bpy.ops.object.mode_set(mode="EDIT")
ebones = arm.data.edit_bones
for eb in ebones:
    if eb.use_deform:
        p = eb.parent
        while p and not p.use_deform:
            p = p.parent
        eb.parent = p
        eb.use_connect = False
for eb in list(ebones):
    if not eb.use_deform:
        ebones.remove(eb)
bpy.ops.object.mode_set(mode="OBJECT")

topo_bones, visited = [], set()
def visit(b):
    if b.name in visited:
        return
    if b.parent:
        visit(b.parent)
    visited.add(b.name)
    topo_bones.append(b.name)
for b in arm.data.bones:
    visit(b)

def blend_mat(ma, mb, t):
    la, qa, sa = ma.decompose()
    lb, qb, sb = mb.decompose()
    if qa.dot(qb) < 0:
        qb = Quaternion((-qb.w, -qb.x, -qb.y, -qb.z))
    return Matrix.LocRotScale(la.lerp(lb, t), qa.slerp(qb, t), sa.lerp(sb, t))

def make_loop(f0, f1, blend_len=6):
    raw = [world_poses[f] for f in range(f0, f1 + 1)]
    n, out = len(raw), []
    for i in range(n):
        if n - 1 - blend_len <= i < n - 1:
            u = (i - (n - 1 - blend_len)) / float(blend_len)
            u = u * u * (3.0 - 2.0 * u)
            out.append({bn: blend_mat(raw[i][bn], raw[0][bn], u) for bn in topo_bones})
        elif i == n - 1:
            out.append({bn: raw[0][bn].copy() for bn in topo_bones})
        else:
            out.append({bn: raw[i][bn].copy() for bn in topo_bones})
    return out

clips_spec = [
    ("SwimLoop", make_loop(382, 416, 6)),
    ("SurfaceCrossing", [world_poses[f] for f in range(388, 413)]),
    ("WaterToCoralTransform", [world_poses[f] for f in range(422, 458)]),
    ("CoralFlightLoop", make_loop(422, 457, 7)),
    ("CoralToWaterDescent", [
        {bn: blend_mat(world_poses[457][bn], world_poses[382][bn], (i / 28.0) ** 2 * (3.0 - 2.0 * (i / 28.0))) for bn in topo_bones}
        for i in range(29)
    ]),
]

arm.animation_data_create()
mw_inv = arm.matrix_world.inverted()
for clip_name, pose_list in clips_spec:
    act = bpy.data.actions.new(name=clip_name)
    arm.animation_data.action = act
    for idx, pose_dict in enumerate(pose_list):
        fn = idx + 1
        sc.frame_set(fn)
        for bn in topo_bones:
            pb = arm.pose.bones[bn]
            pb.matrix = mw_inv @ pose_dict[bn]
            bpy.context.view_layer.update()
            pb.keyframe_insert(data_path="location", frame=fn)
            pb.keyframe_insert(data_path="rotation_quaternion", frame=fn)
            pb.keyframe_insert(data_path="scale", frame=fn)
    tr = arm.animation_data.nla_tracks.new()
    tr.name = clip_name
    st = tr.strips.new(clip_name, 1, act)
    st.name = clip_name

arm.animation_data.action = None
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=DERIV_BLEND)

bpy.ops.export_scene.gltf(
    filepath=GLB_OUT,
    export_format="GLB",
    export_image_format="WEBP",
    export_image_quality=86,
    export_def_bones=True,
    export_animations=True,
    export_animation_mode="NLA_TRACKS",
    export_anim_slide_to_zero=True,
    export_bake_animation=False,
    export_optimize_animation_size=True,
    export_attributes=False,
)

for fn in ["skin_coral_base.webp", "jaw_coral_base.webp", "ventral_coral_base.webp", "claw_coral_base.webp", "tuft_coral_base.webp"]:
    shutil.copy2(os.path.join(TEX_DIR, fn), os.path.join(WEB_TEX_DIR, fn))
for fb in ["kioku-dragon-round35-water-fallback.webp", "kioku-dragon-round35-coral-fallback.webp"]:
    shutil.copy2(os.path.join(TEX_DIR, fb), os.path.join(WEB_MODELS_DIR, fb))
    shutil.copy2(os.path.join(TEX_DIR, fb), os.path.join(WEB_IMG_DIR, fb))

manifest = {
    "assetId": "kioku-round35-dragon-web",
    "sourceMasterBlend": MASTER_BLEND,
    "sourceMasterSha256": EXPECTED_SHA,
    "derivativeBlend": DERIV_BLEND,
    "glbPath": "./assets/models/KIOKU-Dragon-Web.glb",
    "glbBytes": os.path.getsize(GLB_OUT),
    "deformBoneCount": len(topo_bones),
    "meshCount": len(keep_meshes),
    "vertexCount": sum(len(bpy.data.objects[m].data.vertices) for m in keep_meshes),
    "polygonCount": sum(len(bpy.data.objects[m].data.polygons) for m in keep_meshes),
    "clips": [{"name": nm, "frames": len(pl), "fps": 24, "durationSec": round((len(pl) - 1) / 24.0, 4)} for nm, pl in clips_spec],
    "coralTextures": {
        "MAT_Web_Skin": "./assets/models/textures/skin_coral_base.webp",
        "MAT_Web_Jaw": "./assets/models/textures/jaw_coral_base.webp",
        "MAT_Web_Ventral": "./assets/models/textures/ventral_coral_base.webp",
        "MAT_Web_Claw": "./assets/models/textures/claw_coral_base.webp",
        "MAT_Web_Tuft": "./assets/models/textures/tuft_coral_base.webp",
    },
    "fallbacks": {
        "water": "./assets/models/kioku-dragon-round35-water-fallback.webp",
        "coral": "./assets/models/kioku-dragon-round35-coral-fallback.webp",
    },
}
with open(MANIFEST_OUT, "w") as fp:
    json.dump(manifest, fp, indent=2)
print("GLB EXPORT COMPLETE:", json.dumps(manifest, indent=2))
