"""KIOKU River Guardian: refine EXISTING Blender 5.3 scene, never rebuild from scratch.

Usage on the owner's Mac (Blender installed):
  /Applications/Blender.app/Contents/MacOS/Blender --background \
    --python tools/refine_river_guardian_blender.py -- \
    /path/to/KIOKU-River-Guardian-Blender.blend \
    /path/to/output-directory

Outputs an independent edited .blend and review .glb. This script has not been
run in the ChatGPT container because Blender is not installed there.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import bpy

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if not args:
    raise SystemExit('Provide the existing .blend file after --. The original is never modified.')
source=Path(args[0]).expanduser().resolve()
destination=Path(args[1]).expanduser().resolve() if len(args)>1 else source.parent/'kioku-river-refined'
if not source.is_file() or source.suffix.lower()!='.blend':
    raise FileNotFoundError(f'Expected an existing Blender scene: {source}')
destination.mkdir(parents=True,exist_ok=True)
scene_out=destination/'KIOKU-River-Guardian-Refined.blend'
review_out=destination/'KIOKU-River-Guardian-Review.glb'
report_out=destination/'river-guardian-report.json'
if scene_out==source:
    raise RuntimeError('Never overwrite the owner-provided original scene')

bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
armatures=[obj for obj in scene.objects if obj.type=='ARMATURE']
meshes=[obj for obj in scene.objects if obj.type=='MESH']
if not armatures or not meshes:
    raise RuntimeError('Missing rig or mesh in source Blender scene')
rig=max(armatures,key=lambda obj:len(obj.data.bones))
if len(rig.data.bones)!=10:
    raise RuntimeError(f'Expected the owner-approved 10 bone rig; got {len(rig.data.bones)}')
rig.show_in_front=True
rig.display_type='WIRE'

# A conservative visual polish: smooth organic body surfaces only. Keep sharp
# angular details on small eyes, horns and claws that rely on original normals.
smoothed=[]
for obj in meshes:
    if len(obj.data.polygons)>=80:
        for face in obj.data.polygons:
            face.use_smooth=True
        smoothed.append(obj.name)

# Change roughness/metallic without replacing approved material base colors.
look={
    'river blue':(.10,.59),
    'deep outline':(.06,.79),
    'mist highlight':(.06,.49),
    'muted teal':(.08,.61),
    'horn bronze':(.24,.55),
    'eye accent':(.10,.41),
}
updated=[]
for material in bpy.data.materials:
    key=next((key for key in look if key in material.name.lower()),None)
    if key is None:
        continue
    material.use_nodes=True
    bsdf=next((node for node in material.node_tree.nodes if node.type=='BSDF_PRINCIPLED'),None)
    if bsdf is None:
        continue
    metallic,roughness=look[key]
    if 'Metallic' in bsdf.inputs:
        bsdf.inputs['Metallic'].default_value=metallic
    if 'Roughness' in bsdf.inputs:
        bsdf.inputs['Roughness'].default_value=roughness
    updated.append(material.name)

# Honor the six-second swim from the uploaded .blend; do not invent another action.
scene.render.fps=30
scene.frame_start=1
scene.frame_end=180
scene.frame_set(1)
scene['kioku_origin']='Owner-provided River Guardian Blender 5.3 scene'
scene['kioku_release_status']='REVIEW_REQUIRED: shape, weight paint, Safari/WebGL QA'

# Do not silently alter, delete or retarget any animation data or vertex weights.
report={
    'source_blend':str(source),'blender_version':bpy.app.version_string,
    'mesh_objects':[{ 'name':obj.name, 'vertices':len(obj.data.vertices), 'faces':len(obj.data.polygons)} for obj in meshes],
    'rig':rig.name,'bone_count':len(rig.data.bones),
    'actions':[a.name for a in bpy.data.actions],
    'smoothed':smoothed,'materials_refined':updated,
    'render_fps':scene.render.fps,'frame_range':[scene.frame_start,scene.frame_end],
    'note':'Review all anatomical proportions, tail bends and face before Production.'
}
report_out.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(scene_out),compress=True)

# Keep exporter options compatible with Blender versions that rename parameters.
properties={prop.identifier for prop in bpy.ops.export_scene.gltf.get_rna_type().properties}
requested={
    'filepath':str(review_out),'export_format':'GLB',
    'export_animations':True,'export_skins':True,
    'export_normals':True,'export_apply':False,
    'export_cameras':False,'export_lights':False
}
kwargs={k:v for k,v in requested.items() if k in properties}
bpy.ops.export_scene.gltf(**kwargs)
print('KIOKU refined scene:',scene_out)
print('KIOKU review-only GLB:',review_out)
print('Report:',report_out)
print('No Production changes; manual review and real browser GPU checks remain required.')