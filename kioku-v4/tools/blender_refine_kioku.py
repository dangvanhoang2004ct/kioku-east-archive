"""Open the KIOKU GLB prototype for real 3D sculpting and final export in Blender.

Run WITH Blender installed (not available in the ChatGPT execution environment):
    blender --background --python tools/blender_refine_kioku.py

This script imports the user-art-inspired geometric prototype, preserves the
armature and idle action, saves an editable .blend, and exports a review GLB.
Use Blender's Sculpt, Edit, UV, Weight Paint and Pose modes to replace the
rough procedural head/horns/whiskers/feet with production-quality geometry.
DO NOT silently publish the output without reviewing it in Blender first.
"""
import bpy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets'/'models'/'kioku-dragon-rig-v1.glb'
OUT=ROOT/'assets'/'models'/'kioku-dragon-editable.blend'
EXPORT=ROOT/'assets'/'models'/'kioku-dragon-blender-review.glb'

if not SRC.is_file():
    raise RuntimeError(f'Missing KIOKU rigged prototype: {SRC}')

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SRC))

meshes=[obj for obj in bpy.data.objects if obj.type=='MESH']
armatures=[obj for obj in bpy.data.objects if obj.type=='ARMATURE']
if len(meshes)<1 or len(armatures)<1:
    raise RuntimeError('GLB has no mesh or armature; cannot continue')
rig=armatures[0]
rig.name='KIOKU_Dragon_Rig'
rig.display_type='WIRE'
rig.show_in_front=True
for bone in rig.data.bones:
    bone.use_deform=True

for mesh in meshes:
    mesh.name=mesh.name.replace('KIOKU_True3D','KIOKU_Editable')
    mesh.display_type='TEXTURED'
    mesh.select_set(False)
    if not any(mod.type=='ARMATURE' for mod in mesh.modifiers):
        mod=mesh.modifiers.new('KIOKU Armature','ARMATURE')
        mod.object=rig

bpy.context.view_layer.objects.active=rig
rig.select_set(True)
bpy.context.scene.render.fps=30
bpy.context.scene.frame_start=1
bpy.context.scene.frame_end=240  # 8-second seamless idle reference
bpy.context.scene.frame_set(1)

# Save the editable working file first. This is NOT visual QA or finished art.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))

# glTF supports the armature's bone animations, but manual asset review is still
# needed before replacing the current production model.
bpy.ops.export_scene.gltf(
    filepath=str(EXPORT), export_format='GLB',
    export_animations=True, export_skins=True,
    export_apply=False, use_selection=False
)
print(f'KIOKU Blender editable scene saved: {OUT}')
print(f'KIOKU review GLB exported: {EXPORT}')
print('ART DIRECTION TODO: refine face, horns, scale texture, whiskers, claw anatomy, and skin weighting.')