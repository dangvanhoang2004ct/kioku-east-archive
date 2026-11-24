import bpy
import os
import json
import hashlib
import numpy as np

MASTER_BLEND = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/round-35/KIOKU-Dragon-Rebuild.blend"
EXPECTED_SHA = "b766630dabd090fd9db09becb729a5d2bc269c60bd1652334e86cee0ccfecea7"
OUT_DIR = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/web-round35/baked_textures"
MEDIA_DIR = "/Users/dangvanhoang/Documents/kioku-east-archive-main/KIOKU-Creature-Studio/assets/round-35/delivery_media"

os.makedirs(OUT_DIR, exist_ok=True)

h = hashlib.sha256()
with open(MASTER_BLEND, "rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
        h.update(chunk)
actual_sha = h.hexdigest()
assert actual_sha == EXPECTED_SHA, f"Master SHA mismatch: {actual_sha}"
print("Verified Round-35 master SHA-256:", actual_sha)

bpy.ops.wm.open_mainfile(filepath=MASTER_BLEND)

sc = bpy.data.scenes["Scene"]
bpy.context.window.scene = sc
vl = sc.view_layers[0]
sc.frame_set(1)

# Configure Cycles fast 1-sample baking (EMIT and NORMAL are deterministic & noise-free at 1 sample)
sc.render.engine = "CYCLES"
sc.cycles.samples = 1
sc.cycles.use_denoising = False
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    sc.cycles.device = "GPU"
except Exception as e:
    print("Using CPU Cycles:", e)
    sc.cycles.device = "CPU"

def set_realm(state, wet, submerged, emission=1.0):
    for target in (sc, vl):
        target["kioku_state"] = float(state)
        target["kioku_wet"] = float(wet)
        target["kioku_submerged"] = float(submerged)
        target["kioku_fx_emission"] = float(emission)
    sc.update_tag()
    vl.update()
    bpy.context.evaluated_depsgraph_get().update()

# Scale KIOKU_Body_Blockout 5-UDIM UVMap (U in 0..5 -> 0..1) cleanly before baking
body = bpy.data.objects["KIOKU_Body_Blockout"]
uv_layer = body.data.uv_layers["UVMap"]
uv_arr = np.zeros(len(body.data.loops) * 2, dtype=np.float32)
uv_layer.data.foreach_get("uv", uv_arr)
uv_arr = uv_arr.reshape(-1, 2)
uv_arr[:, 0] *= 0.2
uv_layer.data.foreach_set("uv", uv_arr.ravel())
body.data.update()

# Split KIOKU_Eyes into inner eyeball (Sclera+Iris+Pupil) so Cornea outer shell doesn't occlude bake
eyes = bpy.data.objects["KIOKU_Eyes"]
bpy.ops.object.select_all(action="DESELECT")
eyes.select_set(True)
bpy.context.view_layer.objects.active = eyes
# Delete cornea polygons (material_index == 3) on this temporary bake session
import bmesh
bm = bmesh.new()
bm.from_mesh(eyes.data)
cornea_faces = [f for f in bm.faces if f.material_index == 3]
bmesh.ops.delete(bm, geom=cornea_faces, context="FACES")
bm.to_mesh(eyes.data)
bm.free()
eyes.data.update()

def select_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.hide_viewport = False
    obj.hide_render = False
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if obj.data.uv_layers.get("UVMap"):
        obj.data.uv_layers.active = obj.data.uv_layers["UVMap"]
        obj.data.uv_layers["UVMap"].active_render = True

def save_image(img, out_path, fmt="WEBP", color_space="sRGB", quality=88):
    sc.render.image_settings.file_format = fmt
    if fmt == "WEBP":
        sc.render.image_settings.quality = quality
    sc.render.image_settings.color_mode = "RGB"
    sc.display_settings.display_device = "sRGB"
    sc.view_settings.view_transform = "Standard" if color_space == "sRGB" else "Raw"
    sc.view_settings.look = "None"
    img.save_render(filepath=out_path, scene=sc)
    print("Saved:", out_path, os.path.getsize(out_path))

def bake_socket_emit(obj, sock_name, width, height, out_path, fmt="WEBP", is_data=False, quality=88):
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1024:
        loaded = bpy.data.images.load(out_path)
        arr = np.array(loaded.pixels[:], dtype=np.float32)
        bpy.data.images.remove(loaded)
        print("Reusing existing:", out_path)
        return arr
    select_only(obj)
    img = bpy.data.images.new("BakeTmp", width=width, height=height, alpha=False, float_buffer=is_data)
    img.colorspace_settings.name = "Non-Color" if is_data else "sRGB"
    restores = []
    for slot in obj.material_slots:
        mat = slot.material
        if not mat or not mat.node_tree:
            continue
        nt = mat.node_tree
        out_node = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None)
        if not out_node:
            out_node = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if not out_node or not bsdf:
            continue
        orig_surf = out_node.inputs["Surface"].links[0].from_socket if out_node.inputs["Surface"].is_linked else None
        emit = nt.nodes.new("ShaderNodeEmission")
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        for n in nt.nodes:
            n.select = False
        tex.select = True
        nt.nodes.active = tex
        inp = bsdf.inputs[sock_name]
        if inp.is_linked:
            nt.links.new(inp.links[0].from_socket, emit.inputs["Color"])
        else:
            val = inp.default_value
            emit.inputs["Color"].default_value = val if hasattr(val, "__len__") else (val, val, val, 1.0)
        emit.inputs["Strength"].default_value = 1.0
        nt.links.new(emit.outputs["Emission"], out_node.inputs["Surface"])
        restores.append((nt, out_node, orig_surf, emit, tex))

    bpy.ops.object.bake(type="EMIT", margin=8, use_clear=True)
    arr = np.array(img.pixels[:], dtype=np.float32)
    save_image(img, out_path, fmt=fmt, color_space=("Non-Color" if is_data else "sRGB"), quality=quality)

    for nt, out_node, orig_surf, emit, tex in restores:
        if orig_surf:
            nt.links.new(orig_surf, out_node.inputs["Surface"])
        nt.nodes.remove(emit)
        nt.nodes.remove(tex)
    bpy.data.images.remove(img)
    return arr

def bake_normal(obj, width, height, out_path):
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1024:
        print("Reusing existing:", out_path)
        return
    select_only(obj)
    img = bpy.data.images.new("BakeNormTmp", width=width, height=height, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "Non-Color"
    cleanup = []
    for slot in obj.material_slots:
        mat = slot.material
        if not mat or not mat.node_tree:
            continue
        nt = mat.node_tree
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        for n in nt.nodes:
            n.select = False
        tex.select = True
        nt.nodes.active = tex
        cleanup.append((nt, tex))

    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT", margin=8, use_clear=True)
    save_image(img, out_path, fmt="PNG", color_space="Non-Color")
    for nt, tex in cleanup:
        nt.nodes.remove(tex)
    bpy.data.images.remove(img)

# 1. Bake WATER state maps (kioku_state=0.0, natural moist sheen)
set_realm(state=0.0, wet=0.2, submerged=0.0)
skin_w = bake_socket_emit(body, "Base Color", 4096, 1024, os.path.join(OUT_DIR, "skin_water_base.webp"))
bake_socket_emit(body, "Roughness", 2048, 512, os.path.join(OUT_DIR, "skin_roughness.webp"), is_data=True)
bake_normal(body, 4096, 1024, os.path.join(OUT_DIR, "skin_normal.png"))

jaw = bpy.data.objects["KIOKU_LowerJaw"]
bake_socket_emit(jaw, "Base Color", 1024, 1024, os.path.join(OUT_DIR, "jaw_water_base.webp"))
bake_normal(jaw, 1024, 1024, os.path.join(OUT_DIR, "jaw_normal.png"))

ventral = bpy.data.objects["KIOKU_VentralPlates"]
bake_socket_emit(ventral, "Base Color", 1024, 1024, os.path.join(OUT_DIR, "ventral_water_base.webp"))
bake_normal(ventral, 1024, 1024, os.path.join(OUT_DIR, "ventral_normal.png"))

horns = bpy.data.objects["KIOKU_Horns"]
bake_socket_emit(horns, "Base Color", 1024, 1024, os.path.join(OUT_DIR, "horn_base.webp"))
bake_normal(horns, 1024, 1024, os.path.join(OUT_DIR, "horn_normal.png"))

claws = bpy.data.objects["KIOKU_Claws"]
bake_socket_emit(claws, "Base Color", 512, 512, os.path.join(OUT_DIR, "claw_water_base.webp"))

bake_socket_emit(eyes, "Base Color", 1024, 1024, os.path.join(OUT_DIR, "eye_base.webp"), quality=94)
bake_normal(eyes, 1024, 1024, os.path.join(OUT_DIR, "eye_normal.png"))

tuft = bpy.data.objects["KIOKU_TailTuft_Blockout"]
bake_socket_emit(tuft, "Base Color", 512, 512, os.path.join(OUT_DIR, "tuft_water_base.webp"))

# 2. Bake CORAL state maps (kioku_state=1.0)
set_realm(state=1.0, wet=0.06, submerged=0.0)
skin_c = bake_socket_emit(body, "Base Color", 4096, 1024, os.path.join(OUT_DIR, "skin_coral_base.webp"))
bake_socket_emit(jaw, "Base Color", 1024, 1024, os.path.join(OUT_DIR, "jaw_coral_base.webp"))
bake_socket_emit(ventral, "Base Color", 1024, 1024, os.path.join(OUT_DIR, "ventral_coral_base.webp"))
bake_socket_emit(claws, "Base Color", 512, 512, os.path.join(OUT_DIR, "claw_coral_base.webp"))
bake_socket_emit(tuft, "Base Color", 512, 512, os.path.join(OUT_DIR, "tuft_coral_base.webp"))

diff_mean = float(np.mean(np.abs(skin_w - skin_c)))
print("Mean |Water - Coral| on Skin BaseColor:", round(diff_mean, 5))
assert diff_mean > 0.03, f"Water vs Coral skin bake did not diverge enough: {diff_mean}"

# 3. Export optimized WebP fallback posters from authoritative Round-35 renders
for src_name, dst_name in [
    ("underwater_hero_f394.png", "kioku-dragon-round35-water-fallback.webp"),
    ("sky_near_coral_f440.png", "kioku-dragon-round35-coral-fallback.webp"),
]:
    img = bpy.data.images.load(os.path.join(MEDIA_DIR, src_name))
    sc.render.image_settings.file_format = "WEBP"
    sc.render.image_settings.quality = 86
    img.save_render(filepath=os.path.join(OUT_DIR, dst_name), scene=sc)
    bpy.data.images.remove(img)

print("ALL PBR TEXTURES BAKED SUCCESSFULLY.")
