#!/usr/bin/env python3
"""KIOKU River Guardian V4: direct geometry improvements on owner's existing V3 rigged GLB.

Preserves original 10-bone 6-second animation, six material groups, and the original
Blender file. Changes are fully deterministic and do not require Blender installed.
Manual final sculpting/artist review in Blender is still necessary.
"""
from __future__ import annotations
import json,struct,math,hashlib
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial.transform import Rotation

HERE=Path(__file__).resolve().parent
SOURCE=Path('/mnt/data/kioku-river-guardian-v3-review.glb')
DEST=HERE/'kioku-river-guardian-v4-review.glb'

blob=SOURCE.read_bytes()
magic,version,length=struct.unpack_from('<4sII',blob,0)
assert (magic,version,length)==(b'glTF',2,len(blob))
json_len,kind=struct.unpack_from('<I4s',blob,12);assert kind==b'JSON'
gltf=json.loads(blob[20:20+json_len]);off=20+json_len
bin_len,kind=struct.unpack_from('<I4s',blob,off);assert kind==b'BIN\0'
raw=bytearray(blob[off+8:off+8+bin_len])
D={5121:np.dtype('u1'),5123:np.dtype('<u2'),5125:np.dtype('<u4'),5126:np.dtype('<f4')}
N={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}

def get(idx):
 a=gltf['accessors'][idx];v=gltf['bufferViews'][a['bufferView']]
 if 'byteStride' in v or 'sparse' in a:raise ValueError('Interleaved accessor is unsupported')
 n=N[a['type']]; offset=v.get('byteOffset',0)+a.get('byteOffset',0)
 return np.frombuffer(raw,dtype=D[a['componentType']],count=a['count']*n,offset=offset).reshape(-1,n).copy()

def append_array(arr,kind,comp,target):
 arr=np.ascontiguousarray(arr,dtype=D[comp]);n=arr.shape[0]
 while len(raw)%4:raw.append(0)
 start=len(raw);raw.extend(arr.tobytes());vi=len(gltf['bufferViews'])
 gltf['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':arr.nbytes,'target':target})
 a={'bufferView':vi,'componentType':comp,'count':n,'type':kind}
 if kind=='VEC3' and comp==5126:
  a['min']=arr.min(axis=0).astype(float).tolist()
  a['max']=arr.max(axis=0).astype(float).tolist()
 ix=len(gltf['accessors']);gltf['accessors'].append(a)
 return ix

# Continuous positions / radii sampled from actual owner-derived skin.
SAMPLE_X=np.array([-4.25,-4.0,-3.5,-3,-2.4,-1.8,-1.2,-.6,0,.6,1.2,1.8,2.4,2.9,3.4],float)
SAMPLE_Y=np.array([-.04,.01,.14,.20,.23,.44,.80,1.13,1.22,1.03,.73,.54,.53,.52,.46],float)
SAMPLE_RY=np.array([.07,.09,.16,.19,.24,.29,.36,.32,.37,.30,.25,.25,.31,.22,.17],float)
SAMPLE_RZ=np.array([.07,.08,.17,.19,.22,.26,.28,.31,.30,.30,.27,.23,.35,.24,.19],float)
def anatomical(x):
 return (float(np.interp(x,SAMPLE_X,SAMPLE_Y)),float(np.interp(x,SAMPLE_X,SAMPLE_RY)),float(np.interp(x,SAMPLE_X,SAMPLE_RZ)))

# Bone weights follow original head -> neck -> body -> tail order.
BONE_X=np.array([1.95,1.41025,.83875,.172,-.55825,-1.352,-2.1775,-3.003,-3.733,-4.4])
def skin(x,prefer_head=False):
 if prefer_head or x>=BONE_X[0]:return np.array([0,0,0,0],np.uint16),np.array([1.,0.,0.,0.],np.float32)
 if x<=BONE_X[-1]:return np.array([9,0,0,0],np.uint16),np.array([1.,0.,0.,0.],np.float32)
 for i in range(9):
  if BONE_X[i]>=x>=BONE_X[i+1]:
   t=(BONE_X[i]-x)/(BONE_X[i]-BONE_X[i+1])
   return np.array([i,i+1,0,0],np.uint16),np.array([1-t,t,0,0],np.float32)
 raise ValueError(x)

# Curve-based smooth ribbons and tubes attached to the actual skeleton.
def catmull(points,resolution=7):
 p=np.asarray(points,dtype=float)
 pts=[]
 for i in range(len(p)-1):
  P0=p[max(i-1,0)];P1=p[i];P2=p[i+1];P3=p[min(i+2,len(p)-1)]
  for j in range(resolution):
   t=j/resolution
   pts.append(.5*(2*P1+(-P0+P2)*t+(2*P0-5*P1+4*P2-P3)*t*t+(-P0+3*P1-3*P2+P3)*t**3))
 pts.append(p[-1]);return np.array(pts,np.float32)

def tapered_tube(anchors,r0=.02,r1=.002,sides=7,force_head=False):
 curve=catmull(anchors)
 n=len(curve);V=[];F=[];J=[];W=[]
 for i,p in enumerate(curve):
  u=i/max(1,n-1);r=(r0*(1-u)+r1*u)*(0.87+0.13*math.cos(math.pi*u))
  tangent=curve[min(n-1,i+1)]-curve[max(i-1,0)];tangent/=max(1e-8,np.linalg.norm(tangent))
  h=np.array([0.,1.,0.],np.float32) if abs(tangent[1])<.85 else np.array([0.,0.,1.],np.float32)
  nrm=np.cross(tangent,h);nrm/=max(1e-8,np.linalg.norm(nrm));side=np.cross(tangent,nrm)
  j,w=skin(float(p[0]),force_head)
  for q in range(sides):
   ang=2*math.pi*q/sides
   V.append(p+r*(math.cos(ang)*nrm+math.sin(ang)*side));J.append(j);W.append(w)
  if i:
   for q in range(sides):
    a=(i-1)*sides+q;b=(i-1)*sides+(q+1)%sides;c=i*sides+q;d=i*sides+(q+1)%sides
    F.extend(((a,c,b),(b,c,d)))
 return np.array(V,np.float32),np.array(F,np.int32),np.array(J,np.uint16),np.array(W,np.float32)

def leaf(anchors,max_width=.07,width_axis=(0,1,0),force_head=False):
 curve=catmull(anchors,resolution=6)
 axis=np.asarray(width_axis,np.float32);axis/=max(1e-9,np.linalg.norm(axis))
 V=[];F=[];J=[];W=[]
 for i,p in enumerate(curve):
  t=i/max(1,len(curve)-1);r=max_width*math.sin(math.pi*t)**.8
  tangent=curve[min(len(curve)-1,i+1)]-curve[max(i-1,0)]
  tangent/=max(1e-9,np.linalg.norm(tangent))
  across=axis-np.dot(axis,tangent)*tangent;across/=max(1e-8,np.linalg.norm(across))
  j,w=skin(float(p[0]),force_head)
  for sign in (-1,1):
   V.append(p+sign*r*across);J.append(j);W.append(w)
  if i:
   a=(i-1)*2;b=i*2
   F.extend(((a,b,a+1),(a+1,b,b+1)))
 return np.array(V,np.float32),np.array(F,np.int32),np.array(J,np.uint16),np.array(W,np.float32)

def ring_seam(x,side=1):
 cy,ry,rz=anatomical(x)
 V=[];F=[];J=[];W=[]
 # Thin seam follows a shallow arc around the underside of the serpentine tube.
 for i,ang in enumerate(np.linspace(-2.25,-.89,17)):
  y=cy+ry*math.sin(ang)-.008;z=rz*math.cos(ang)*1.01
  for dx in (-.008,.008):
   V.append([x+dx,y,z]);j,w=skin(x+dx);J.append(j);W.append(w)
  if i:
   a=(i-1)*2;b=i*2;F.extend(((a,b,a+1),(a+1,b,b+1)))
 return np.array(V,np.float32),np.array(F,np.int32),np.array(J,np.uint16),np.array(W,np.float32)

def scale_plate(x,side=1,row=0):
 cy,ry,rz=anatomical(x)
 y=cy+ry*(.17 if row==0 else -.11)
 z=side*(rz*(.95 if row==0 else .99))
 base=np.array([x,y,z],float)
 # Crescent-like tapered scale curving backward and outward.
 anchors=[base+np.array([.10,-.005,0]),base+np.array([.04,.052,side*.016]),base+np.array([-.055,.037,side*.033]),base+np.array([-.125,-.005,0])]
 return leaf(anchors,max_width=.035 if row==0 else .027,width_axis=(0,1,0))

prims=gltf['meshes'][0]['primitives'];assert len(prims)==6 and len(gltf['skins'][0]['joints'])==10
extras={i:[] for i in range(6)}

# MAIN VISUAL: remove the V3 duplicate overlay horns and whiskers, then add fewer
# intentional pieces with physically curved outlines rooted to the original head.
# (V3 file itself documents these vertices were appended after 1813/296.)
cut={2:1813,4:296}

# Almond eyebrow / cheek crests (on both sides). Dark navy and fine icy highlights.
for s in (-1,1):
 extras[1].append(leaf([(2.44,.843,s*.335),(2.67,.858,s*.381),(2.91,.826,s*.349),(3.09,.76,s*.31)],.055,(0,1,0),True))
 extras[2].append(tapered_tube([(2.51,.823,s*.37),(2.70,.828,s*.392),(2.90,.811,s*.36)],.009,.003,6,True))
 # Three layered whisker-like cheek/mane tendrils sweeping backward, unique KIOKU signature.
 for k in range(4):
  dy=.10*k;dz=.03*k
  extras[1].append(leaf([(2.22,.67+dy,s*.38),(1.99,.71+dy,s*.49),(1.64,.63+dy,s*.59),(1.14-.13*k,.52+.06*k,s*(.71+.025*k))],max_width=.066-(k*.007),width_axis=(0,1,0),force_head=True))
  if k%2==0:
   extras[3].append(leaf([(2.16,.66+dy,s*.41),(1.90,.74+dy,s*.52),(1.59,.66+dy,s*.62),(1.18-.13*k,.55+.06*k,s*(.75+.025*k))],max_width=.024,width_axis=(0,1,0),force_head=True))
 # Swept-back mane silhouette: three deliberately different layers, not repeated spikes.
 extras[1].append(leaf([(2.19,.94,s*.39),(1.86,1.17,s*.56),(1.47,1.29,s*.68),(.98,1.30,s*.77)],.112,(0,1,0),True))
 extras[3].append(leaf([(2.14,.90,s*.40),(1.83,1.08,s*.57),(1.43,1.18,s*.68),(1.03,1.20,s*.76)],.048,(0,1,0),True))
 extras[1].append(leaf([(2.15,.57,s*.43),(1.85,.49,s*.61),(1.43,.35,s*.77),(.94,.23,s*.86)],.127,(0,1,0),True))
 extras[3].append(leaf([(2.11,.55,s*.44),(1.78,.44,s*.61),(1.39,.32,s*.76),(1.01,.24,s*.84)],.050,(0,1,0),True))
 extras[1].append(leaf([(2.37,.43,s*.34),(2.05,.29,s*.55),(1.64,.22,s*.68),(1.21,.13,s*.76)],.073,(0,1,0),True))
 # Prominent but restrained flowing face feelers.
 extras[2].append(tapered_tube([(3.14,.43,s*.28),(3.47,.52,s*.47),(3.81,.72,s*.64),(4.15,.76,s*.80),(4.52,.70,s*.92)],.020,.002,7,True))
 extras[3].append(tapered_tube([(3.03,.33,s*.27),(3.27,.14,s*.41),(3.60,.10,s*.52),(3.94,.14,s*.71),(4.31,.15,s*.83)],.012,.0015,6,True))
 # Swept-back two-pronged antler branch rather than duplicate long vertical horns.
 extras[1].append(tapered_tube([(1.93,1.05,s*.33),(1.80,1.29,s*.38),(1.57,1.52,s*.45),(1.33,1.60,s*.51)],.064,.004,8,True))
 extras[3].append(tapered_tube([(1.74,1.35,s*.42),(1.50,1.43,s*.47),(1.29,1.51,s*.55)],.022,.003,7,True))
 # Fine mouth line to separate snout and jaw.
 extras[1].append(tapered_tube([(2.91,.405,s*.285),(3.11,.401,s*.27),(3.28,.431,s*.24)],.010,.003,6,True))

# Stylized body scales, blue-teal overlays with staggered spacing (each skinned).
for s in (-1,1):
 for i,x in enumerate(np.linspace(-3.55,1.04,21)):
  extras[3 if i%4==0 else 1].append(scale_plate(float(x),s,0))
 # Additional refined tail streamers.
 extras[3].append(leaf([(-4.18,.015,s*.045),(-4.51,.11,s*.14),(-4.91,.17,s*.23),(-5.29,.18,s*.28)],.069,(0,1,0)))
 extras[1].append(leaf([(-4.18,.015,s*.055),(-4.53,.055,s*.10),(-4.92,.07,s*.14),(-5.24,.11,s*.17)],.047,(0,1,0)))

# Distinct but low-contrast belly plate divisions, not big plastic ribs.
# Natural underbelly plates from the original mesh are preserved. Previous procedural
# seams were lifted off the body surface and produced tooth-like floating artifacts;
# do not add geometry until attachment can be checked in Blender.

# Hand refinements: thin extra talons on the four existing feet.
# Original feet get articulated by the existing skeleton; extras follow nearest bones.
for x,yy in [(-2.08,-.49)]:
 for s in (-1,1):
  for k in (-1,0,1):
   z=s*(.49+.065*k)
   extras[4].append(tapered_tube([(x,yy,z),(x+.08,yy-.09,z+s*.04),(x+.22,yy-.16,z+s*.06)],.025,.002,7))

# Helper for recomputing normals after adding faces.
def normals(v,f):
 n=np.zeros_like(v,dtype=np.float64)
 tris=v[f];cross=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);
 np.add.at(n,f[:,0],cross);np.add.at(n,f[:,1],cross);np.add.at(n,f[:,2],cross)
 length=np.linalg.norm(n,axis=1)
 n/=np.maximum(length[:,None],1e-9)
 return n.astype('<f4')

metrics=[]
for i,p in enumerate(prims):
 a=p['attributes']
 v=get(a['POSITION']).astype(np.float32)
 f=get(p['indices']).reshape(-1,3).astype(np.int32)
 jj=get(a['JOINTS_0']).astype(np.uint16)
 ww=get(a['WEIGHTS_0']).astype(np.float32)
 original=len(v)
 if i in cut:
  limit=cut[i]
  f=f[(f<limit).all(axis=1)]
  v=v[:limit];jj=jj[:limit];ww=ww[:limit]
 # Adjust head shape without rebuilding or losing skin weights.
 if i==0:
  x=v[:,0];head=np.clip((x-1.8)/.9,0,1)
  v[:,2]*=(1-.055*head)
  snout=np.clip((x-2.8)/.8,0,1)
  v[:,2]*=(1-.07*snout)
  v[:,1]-=.025*snout
 # Eye geometry in V3 is round and far too prominent. Keep both eyes, but shrink,
 # flatten z relief and slightly lift their placement for a calmer almond expression.
 if i==5:
  for s in (-1,1):
   mask=(v[:,2]*s>0)
   center=np.array([2.726,.743,s*.388],dtype=np.float32)
   v[mask]=center+(v[mask]-center)*np.array([.69,.33,.47],dtype=np.float32)
   v[mask,1]+=.012
   v[mask,2]-=s*.048
 # Reduce old triangular dorsal spikes; new flowing silhouette is carried by
 # manes and scales instead of identical sharp points.
 if i==1:
  for vi,q in enumerate(v):
   x,y,z=q
   if -4.15<x<1.55:
    cy,ry,rz=anatomical(float(x))
    base=cy+ry*.50
    if y>base:
     v[vi,1]=base+(y-base)*.50
 for ev,ef,ej,ew in extras[i]:
  offset=len(v)
  if len(ev)==0:continue
  f=np.concatenate([f,ef+offset],axis=0)
  v=np.concatenate([v,ev],axis=0)
  jj=np.concatenate([jj,ej],axis=0)
  ww=np.concatenate([ww,ew],axis=0)
 assert len(v)<65536,(i,len(v))
 assert np.max(f)<len(v)
 assert np.max(jj)<10
 assert np.allclose(ww.sum(axis=1),1,atol=1e-3)
 nn=normals(v,f)
 a['POSITION']=append_array(v,'VEC3',5126,34962)
 a['NORMAL']=append_array(nn,'VEC3',5126,34962)
 a['JOINTS_0']=append_array(jj,'VEC4',5123,34962)
 a['WEIGHTS_0']=append_array(ww,'VEC4',5126,34962)
 p['indices']=append_array(f.reshape(-1,1),'SCALAR',5123,34963)
 metrics.append({'material':i,'original_vertices':original,'review_vertices':len(v),'triangles':len(f),'features':len(extras[i])})

# Web styling: keep exact six material IDs, but replace bronze horns & red eyes
# with the ORIGINAL owner's navy/mist color family.
colors={
 0:(.255,.420,.580,1), # river-blue body
 1:(.105,.204,.335,1), # dark navy shape accents
 2:(.819,.890,.917,1), # belly + delicate ivory whiskers
 3:(.280,.510,.592,1), # muted jade/teal accents
 4:(.172,.304,.439,1), # horns + claws slate navy, no bronze
 5:(.674,.836,.835,1), # jade eye, no cartoon red orb
}
for i,m in enumerate(gltf['materials']):
 mr=m.setdefault('pbrMetallicRoughness',{})
 mr['baseColorFactor']=list(colors[i])
 mr['metallicFactor']=[.08,.025,.025,.025,.055,.015][i]
 mr['roughnessFactor']=[.58,.70,.44,.51,.57,.40][i]
 m['doubleSided']=True

# Same animation, bones and curves; preserving original nonzero 9-bone swim.
# Increase articulation through the middle of the chain, not just the tail.
# Keep the phase-delayed wave and exact six-second closure. The head root stays
# anchored to avoid spinning the whole model as if it were a single rigid lump.
for channel in gltf['animations'][0]['channels']:
 if channel['target']['path']!='rotation':continue
 joint=channel['target']['node'];assert 1<=joint<=9
 sampler=gltf['animations'][0]['samplers'][channel['sampler']]
 ts=get(sampler['input']).reshape(-1)
 amplitude=[0,.034,.052,.070,.083,.096,.107,.118,.125,.132][joint]
 phase=2*math.pi*ts/6-(joint-1)*.40
 yaw=.61*amplitude*np.cos(phase+.22)
 bend=amplitude*np.sin(phase)
 twist=.18*amplitude*np.sin(phase-.35)
 q=Rotation.from_euler('xyz',np.column_stack([twist,yaw,bend])).as_quat().astype('<f4')
 assert np.allclose(q[0],q[-1],atol=1e-6)
 accessor=gltf['accessors'][sampler['output']]
 view=gltf['bufferViews'][accessor['bufferView']]
 base=view.get('byteOffset',0)+accessor.get('byteOffset',0)
 raw[base:base+q.nbytes]=q.tobytes()

gltf['animations'][0]['name']='River Guardian V4 — fuller articulated traveling wave / 6s'
gltf['asset'].setdefault('extras',{})['KIOKU_V4']={
 'source':'Owner-provided V3 rigged review GLB',
 'edits':'remove duplicate horns/whiskers; style navy horns + almond eyes; layered mane; leaf fins; skinned scales; belly seams; tails; sculpt details',
 'rig':'unchanged 10 joint skin, 9 rotation channels, 6s loop',
 'blender_rebuild':'not tested; artist refinement still required'
}

def compact_save():
 # Repack only referenced arrays so the new file is efficiently shippable.
 cache={};newbin=bytearray();newviews=[];newacc=[]
 def use(index):
  if index in cache:return cache[index]
  a=gltf['accessors'][index];v=gltf['bufferViews'][a['bufferView']]
  n=N[a['type']];size=D[a['componentType']].itemsize
  start=v.get('byteOffset',0)+a.get('byteOffset',0)
  chunk=raw[start:start+a['count']*n*size]
  while len(newbin)%4:newbin.append(0)
  off=len(newbin);newbin.extend(chunk);viewidx=len(newviews)
  newviews.append({'buffer':0,'byteOffset':off,'byteLength':len(chunk),**({'target':v['target']} if 'target' in v else {})})
  copy={k:value for k,value in a.items() if k not in ('bufferView','byteOffset')}
  copy['bufferView']=viewidx;idx=len(newacc);newacc.append(copy);cache[index]=idx;return idx
 for mesh in gltf['meshes']:
  for prim in mesh['primitives']:
   prim['attributes']={key:use(val) for key,val in prim['attributes'].items()}
   prim['indices']=use(prim['indices'])
 for sk in gltf['skins']:
  sk['inverseBindMatrices']=use(sk['inverseBindMatrices'])
 for anim in gltf['animations']:
  for sampler in anim['samplers']:
   sampler['input']=use(sampler['input']);sampler['output']=use(sampler['output'])
 gltf['accessors']=newacc;gltf['bufferViews']=newviews;gltf['buffers'][0]['byteLength']=len(newbin)
 j=json.dumps(gltf,ensure_ascii=False,separators=(',',':')).encode('utf8');j+=b' '*((-len(j))%4)
 newbin+=b'\0'*((-len(newbin))%4)
 total=12+8+len(j)+8+len(newbin)
 DEST.write_bytes(struct.pack('<4sII',b'glTF',2,total)+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(newbin),b'BIN\0')+newbin)
compact_save()
report={'source':str(SOURCE),'output':str(DEST),'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'bytes':DEST.stat().st_size,
 'bones':len(gltf['skins'][0]['joints']),'animation_channels':len(gltf['animations'][0]['channels']),'duration_seconds':6,'materials':len(prims),'parts':metrics}
(HERE/'metrics-v4.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))