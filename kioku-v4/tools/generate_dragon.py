"""KIOKU prototype: a full 3D skinned Eastern dragon in one glTF/GLB.

Geometry is procedural (not a 2D billboard). All vertices have joints/weights;
a hierarchical 11-bone armature is embedded with a seamless 8s idle animation.
Artwork is APPROXIMATED from the owner's source reference; not a hand-sculpted
exact reproduction. Blender can import the resulting .glb and refine the model.
Dependencies: numpy (available locally), stdlib only otherwise.
"""
import math, json, struct, pathlib
import numpy as np

OUT=pathlib.Path(__file__).resolve().parents[1]/'assets/models/kioku-dragon-rig-v1.glb'
OUT.parent.mkdir(parents=True,exist_ok=True)
PI=math.pi
TAU=2*PI
VERT=[]; COLOR=[]; IDX=[]
COLORS={
 'body':(0.055,0.18,0.34,1), 'body2':(.075,.29,.48,1),
 'body3':(.12,.38,.57,1),'belly':(.70,.85,.89,1),'belly2':(.52,.73,.8,1),
 'mane':(.05,.12,.29,1),'mane2':(.11,.27,.45,1),
 'horn':(.12,.22,.38,1),'horn_tip':(.31,.53,.62,1),
 'eye':(.90,.88,.65,1),'pupil':(.03,.08,.13,1),'claw':(.08,.16,.32,1),
 'accent':(.22,.55,.61,1),'jaw':(.26,.46,.61,1),
}


def vec(*x):return np.array(x,dtype=np.float64)
def norm(v):
 n=float(np.linalg.norm(v));return v/max(n,1e-8)
def mix(a,b,t):return a*(1-t)+b*t

def add_vert(p,c):
 VERT.append(list(map(float,p)))
 COLOR.append(COLORS.get(c,c))
 return len(VERT)-1

def tri(a,b,c):IDX.extend([a,b,c])

def curve(s):
 s=float(s)
 return vec(-3.85+7.5*s, .60*math.sin(TAU*(1.22*s)+.33)-.05, .25*math.sin(TAU*.86*s+.35))

def tangent(s):return norm(curve(min(1,s+.001))-curve(max(0,s-.001)))

def ring_axes(tan):
 right=norm(np.cross(tan,vec(0,1,0)))
 if np.linalg.norm(right)<.01:right=vec(0,0,1)
 up=norm(np.cross(right,tan))
 return up,right

def tube(fn, radius_fn, rings, sides, color_fn, cap=True):
 first=len(VERT)
 for i in range(rings+1):
  s=i/rings; p=fn(s)
  d=norm(fn(min(1,s+1e-3))-fn(max(0,s-1e-3)))
  up,right=ring_axes(d)
  for j in range(sides+1):
   angle=j/sides*TAU
   rad=(up*math.cos(angle)+right*math.sin(angle))*radius_fn(s)
   add_vert(p+rad,color_fn(s,angle))
 for i in range(rings):
  for j in range(sides):
   a=first+i*(sides+1)+j;b=a+(sides+1)
   tri(a,b,a+1);tri(b,b+1,a+1)
 if cap:
  for s,sign in [(0,-1),(1,1)]:
   center=add_vert(fn(s),color_fn(s,0));base=first+(rings if s==1 else 0)*(sides+1)
   for j in range(sides):
    if sign==-1:tri(center,base+j+1,base+j)
    else:tri(center,base+j,base+j+1)

def ellipsoid(center,radii,color,rings=14,sides=24):
 first=len(VERT)
 for i in range(rings+1):
  th=PI*i/rings
  for j in range(sides+1):
   ph=TAU*j/sides
   n=vec(math.sin(th)*math.cos(ph),math.cos(th),math.sin(th)*math.sin(ph))
   add_vert(center+n*radii,color)
 for i in range(rings):
  for j in range(sides):
   a=first+i*(sides+1)+j;b=a+sides+1
   tri(a,b,a+1);tri(b,b+1,a+1)

def fin(a,b,c,color,depth=.045):
 a=np.asarray(a);b=np.asarray(b);c=np.asarray(c)
 n=norm(np.cross(b-a,c-a))
 ia=add_vert(a+n*depth,color);ib=add_vert(b+n*depth,color);ic=add_vert(c+n*depth,color)
 idd=add_vert(a-n*depth,color);ie=add_vert(b-n*depth,color);iff=add_vert(c-n*depth,color)
 tri(ia,ib,ic);tri(idd,iff,ie)
 for x,y,z,w in [(ia,idd,ib,ie),(ib,ie,ic,iff),(ic,iff,ia,idd)]:
  tri(x,z,y);tri(y,z,w)

# BODY - a substantial closed, sculptural volume, NOT a flat plane.
def body_radius(s):
 return .065+.28*(max(0,math.sin(PI*(.04+.94*s)))**.45)
def color_body(s,ang):
 belly=math.cos(ang)<-.35
 if belly:return 'belly' if int(s*29)%2==0 else 'belly2'
 if math.cos(ang)>.75 and int(s*55)%3==0:return 'body3'
 return 'body' if int(s*45)%3 else 'body2'
tube(curve,body_radius,192,20,color_body)

# Segmented dorsal crest and low swept fins: tapered, closed 3D volumes.
for i in range(9,188,5):
 s=i/192;p=curve(s);d=tangent(s);up,right=ring_axes(d)
 h=.12+.09*math.sin(PI*s)
 fin(p+up*body_radius(s)*.88-d*.09,p+up*(body_radius(s)+h),p+up*body_radius(min(1,s+.028))*.86+d*.20,'mane2',.028)

# Facial volumes match the blue elongated oriental-dragon proportions.
head=curve(1)+vec(.13,.10,0)
ellipsoid(head+vec(.18,.04,0),vec(.53,.29,.33),'body2',18,28)
ellipsoid(head+vec(.60,-.07,0),vec(.46,.155,.24),'jaw',12,22)
ellipsoid(head+vec(.54,.04,0),vec(.44,.18,.265),'body3',12,22)
# cheek / whisker bases, eyebrows and eyes on both sides
for side in [-1,1]:
 ellipsoid(head+vec(.26,.15,side*.31),vec(.10,.055,.057),'horn',10,14)
 ellipsoid(head+vec(.31,.16,side*.356),vec(.054,.04,.035),'eye',9,12)
 ellipsoid(head+vec(.34,.16,side*.384),vec(.022,.025,.014),'pupil',7,9)
 fin(head+vec(.13,.22,side*.30),head+vec(-.25,.35,side*.42),head+vec(-.10,.05,side*.37),'mane',.032)
 # Horns antlers, locally tapered curved tube, strongly three dimensional.
 horn_base=head+vec(-.14,.23,side*.21)
 def horn(t,base=horn_base,side=side):
  return base+vec(-.47*t-.10*t*t,.62*t+.14*math.sin(PI*t),side*(.10*t+.16*t*t))
 tube(horn,lambda t:.065*(1-t)+.006,22,9,lambda t,a:'horn' if t<.75 else 'horn_tip')
 # Branch on each horn.
 branch=horn(.51)
 tube(lambda t,b=branch,side=side:b+vec(.10*t,.18*t,side*.20*t),lambda t:.038*(1-t)+.003,12,7,lambda t,a:'horn_tip')
 # Flowing long whiskers.
 sn=head+vec(.80,-.03,side*.16)
 for k in range(2):
  tube(lambda t,sn=sn,side=side,k=k:sn+vec(.73*t+.05*k*t,.11*math.sin(PI*t)-(.20+.10*k)*t,side*(.19*t+.03*math.sin(TAU*t))),
   lambda t:(.014-.005*k)*(1-t)+.002,32,6,lambda t,a:'accent',False)
 # Mane around ears directed back, individual tapered feathers.
 for k in range(4):
  st=head+vec(-.10-.11*k,.14-.035*k,side*(.18+.04*k))
  fin(st,st+vec(-.38-.10*k,.27-.04*k,side*(.13+.02*k)),st+vec(-.53-.10*k,-.03,side*.16),'mane' if k%2 else 'mane2',.04)

# Tail leaflets and a dramatic tapered fan.
tail=curve(0)
for side in [-1,0,1]:
 fin(tail+vec(-.02,.04,side*.05),tail+vec(-.38,-.15+side*.08,side*.20),tail+vec(-.75,-.1+side*.14,side*.3),'mane' if side else 'body2',.022)

# Tiny limbs and hooked claws mounted to body at two sections.
for s in [.69,.88]:
 p=curve(s)
 for side in [-1,1]:
  shoulder=p+vec(0,-.02,side*.19)
  elbow=shoulder+vec(.11,-.32,side*.25)
  palm=elbow+vec(.17,-.18,side*.07)
  tube(lambda t,a=shoulder,b=elbow:mix(a,b,t),lambda t:.09-.015*t,9,9,lambda t,a:'body',True)
  tube(lambda t,a=elbow,b=palm:mix(a,b,t),lambda t:.07-.025*t,9,8,lambda t,a:'body2',True)
  for k in [-1,0,1]:
   toe=palm+vec(.16,-.10,k*.10)
   tip=toe+vec(.13,-.075,k*.024)
   tube(lambda t,a=palm,b=toe,c=tip:mix(mix(a,b,min(1,t*1.4)),c,max(0,(t-.6)/.4)),
       lambda t:.034*(1-t)+.003,12,6,lambda t,a:'claw',True)

P=np.asarray(VERT,dtype=np.float32)
F=np.asarray(IDX,dtype=np.uint16).reshape(-1,3)
COL=np.asarray(COLOR,dtype=np.float32)
assert len(P)<65000 and len(P)==len(COL)
# Compute smooth vertex normals from adjacent indexed faces (triangle winding).
N=np.zeros_like(P)
for a,b,c in F:
 aa,bb,cc=P[[a,b,c]]
 nn=np.cross(bb-aa,cc-aa)
 N[a]+=nn;N[b]+=nn;N[c]+=nn
N/=np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-7)
# Interpolate bone weights along the length of the single body.
BONE_COUNT=11
bind_centers=np.asarray([curve(1-i/(BONE_COUNT-1)) for i in range(BONE_COUNT)],dtype=np.float64)
joint=np.zeros((len(P),4),dtype=np.uint16)
weight=np.zeros((len(P),4),dtype=np.float32)
for i,p in enumerate(P):
 s=float(np.clip((p[0]+3.85)/7.5,0,1))
 a=(1-s)*(BONE_COUNT-1);j0=min(int(math.floor(a)),BONE_COUNT-1);j1=min(j0+1,BONE_COUNT-1)
 blend=a-j0 if j0!=j1 else 0
 joint[i,:2]=j0,j1;weight[i,:2]=1-blend,blend
assert np.allclose(weight.sum(axis=1),1)

# Matrix convention glTF: column-major 4x4 float arrays.
IBM=np.array([np.array([[1,0,0,-p[0]],[0,1,0,-p[1]],[0,0,1,-p[2]],[0,0,0,1]],dtype=np.float32).T.flatten() for p in bind_centers],dtype=np.float32)

def quat_z_y(z,y):
 sz,cz=math.sin(z/2),math.cos(z/2)
 sy,cy=math.sin(y/2),math.cos(y/2)
 # q_z * q_y
 return [-sz*sy,cz*sy,sz*cy,cz*cy]

DURATION=8.0
T=np.linspace(0,DURATION,33,dtype=np.float32)
ROT=[]
for i in range(BONE_COUNT):
 amp=.006+i*.0023
 arr=[]
 for tt in T:
  angle=TAU*float(tt)/DURATION-.48*i
  yaw=.35*amp*math.sin(angle+1.2)
  turn=amp*math.sin(angle)
  arr.append(quat_z_y(turn,yaw))
 ROT.append(np.array(arr,dtype=np.float32))

# Minimal binary glTF buffer and metadata builder.
BIN=bytearray(); VIEWS=[]; ACCESS=[]
C={np.dtype('float32'):5126,np.dtype('uint16'):5123,np.dtype('uint32'):5125}
TYP={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}

def append_acc(data,typ,target=None,limits=False):
 data=np.ascontiguousarray(data)
 align=(-len(BIN))%4
 if align:BIN.extend(b'\x00'*align)
 offset=len(BIN);raw=data.tobytes();BIN.extend(raw)
 view={'buffer':0,'byteOffset':offset,'byteLength':len(raw)}
 if target is not None:view['target']=target
 vi=len(VIEWS);VIEWS.append(view)
 count=data.size//TYP[typ]
 acc={'bufferView':vi,'componentType':C[data.dtype],'count':count,'type':typ}
 if limits:
  flat=data.reshape(count,-1)
  acc['min']=flat.min(axis=0).astype(float).tolist();acc['max']=flat.max(axis=0).astype(float).tolist()
 ai=len(ACCESS);ACCESS.append(acc);return ai

acc_pos=append_acc(P,'VEC3',34962,True)
acc_nor=append_acc(N,'VEC3',34962)
acc_col=append_acc(COL,'VEC4',34962)
acc_jo=append_acc(joint,'VEC4',34962)
acc_w=append_acc(weight,'VEC4',34962)
acc_index=append_acc(np.asarray(IDX,dtype=np.uint16),'SCALAR',34963)
acc_ibm=append_acc(IBM,'MAT4')
acc_time=append_acc(T,'SCALAR',None,True)
acc_rot=[append_acc(x,'VEC4') for x in ROT]

# Node #0 is skinned mesh. Node #1..11 are armature joints.
NODES=[{'name':'KIOKU_Dragon_Mesh','mesh':0,'skin':0,'extras':{'role':'owner-inspired sculpt'}}]
for i,p in enumerate(bind_centers):
 relative=p if i==0 else p-bind_centers[i-1]
 node={'name':('Head_Root' if i==0 else ('Neck_%02d'%i if i<4 else ('Body_%02d'%i if i<8 else 'Tail_%02d'%i))),
       'translation':[float(x) for x in relative]}
 if i+1<BONE_COUNT:node['children']=[i+2]
 NODES.append(node)

samplers=[{'input':acc_time,'output':acc,'interpolation':'LINEAR'} for acc in acc_rot]
channels=[{'sampler':i,'target':{'node':i+1,'path':'rotation'}} for i in range(BONE_COUNT)]
GLTF={
 'asset':{'version':'2.0','generator':'KIOKU procedural 3D reference prototype','copyright':'KIOKU original dragon illustration source'},
 'scene':0,'scenes':[{'nodes':[0,1]}],'nodes':NODES,
 'meshes':[{'name':'KIOKU_True3D_SkinnedDragon','primitives':[{'attributes':{
  'POSITION':acc_pos,'NORMAL':acc_nor,'COLOR_0':acc_col,'JOINTS_0':acc_jo,'WEIGHTS_0':acc_w},
  'indices':acc_index,'material':0,'mode':4}]}],
 'materials':[{'name':'KIOKU_Blue_Ice','pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':.16,'roughnessFactor':.54},'doubleSided':True}],
 'skins':[{'name':'KIOKU_Spine_11_Bones','inverseBindMatrices':acc_ibm,'joints':list(range(1,BONE_COUNT+1)),'skeleton':1}],
 'animations':[{'name':'Idle_8s_Subtle_Undulation','samplers':samplers,'channels':channels}],
 'accessors':ACCESS,'bufferViews':VIEWS,'buffers':[{'byteLength':len(BIN)}],
 'extras':{'prototype':True,'designSource':'KIOKU owner supplied blue dragon logo','limitations':'Procedural approximation; not hand-sculpted in Blender'}
}
JS=json.dumps(GLTF,separators=(',',':')).encode('utf8');JS+=b' '*((-len(JS))%4)
BIN+=b'\x00'*((-len(BIN))%4)
filebytes=12+8+len(JS)+8+len(BIN)
glb=bytearray(struct.pack('<4sII',b'glTF',2,filebytes));glb.extend(struct.pack('<I4s',len(JS),b'JSON'));glb.extend(JS)
glb.extend(struct.pack('<I4s',len(BIN),b'BIN\x00'));glb.extend(BIN)
assert len(glb)==filebytes
OUT.write_bytes(glb)
print(json.dumps({'output':str(OUT),'vertices':len(P),'triangles':len(F),'bones':BONE_COUNT,'duration':DURATION,'bytes':filebytes,'bounds':{'min':P.min(axis=0).tolist(),'max':P.max(axis=0).tolist()}},indent=2))