"""Measured CAD (not physical) clearances; run after prepare_inputs.py with CadQuery 2.6.1.
No edits to source PCB. STEP coordinate units are read by OpenCascade (mm).
"""
import argparse,hashlib,json,math,os,pathlib,sys
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
p=argparse.ArgumentParser();p.add_argument('--scratch',required=True);p.add_argument('--output',default=str(pathlib.Path(__file__).parent/'cad_evidence.json'));a=p.parse_args();w=pathlib.Path(a.scratch)
sha=lambda f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
def box(s):
 b=s.BoundingBox();return [b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax]
def load(n):return cq.importers.importStep(str(w/n)).val()
def measure(x,y,boolean=True):
 d=BRepExtrema_DistShapeShape(x.wrapped,y.wrapped);d.Perform();assert d.IsDone()
 u=d.PointOnShape1(1);v=d.PointOnShape2(1)
 r=dict(minimum_distance_mm=d.Value(),point_a=[u.X(),u.Y(),u.Z()],point_b=[v.X(),v.Y(),v.Z()])
 if boolean:r['intersection_volume_mm3']=x.intersect(y).Volume()
 return r
host=load('official_radxa.stp');c45=load('c45.step');board=load('board.step');bottom=load('bottom.step');surfaces=load('surfaces.step')
inputs=json.loads((w/'inputs.json').read_text());j4=next(r for r in inputs['footprints'] if r['ref']=='J4')
e=dict(inputs={k:v for k,v in inputs.items() if k!='footprints'},cadquery=cq.__version__,units='mm',limitations=['CAD measurements only, not physical measurements','Generic KiCad bodies are not exact supplier part tolerances','J4 intentionally excluded; not exact model; no connector stack approval','Y1 missing model; U4 DNP excluded; top components and cables not reviewed','Official host is a fused simplified CAD assembly; part names not recovered','No screw/spacer models, bow, solder tolerances, heatsink or RF analysis'],exports={n:dict(sha256=sha(w/n),bbox_mm=box(s),solids=len(s.Solids())) for n,s in [('official_radxa.stp',host),('c45.step',c45),('board.step',board),('bottom.step',bottom),('surfaces.step',surfaces)]})
mounts=[];pins=[];large=[]
for i,f in enumerate(host.Faces()):
 b=f.BoundingBox()
 if f.Area()>500:
  ad=BRepAdaptor_Surface(f.wrapped);plane=ad.Plane() if f.geomType()=='PLANE' else None
  large.append(dict(face=i,type=f.geomType(),area_mm2=f.Area(),bbox_mm=box(f),plane_origin_mm=[plane.Location().X(),plane.Location().Y(),plane.Location().Z()] if plane else None))
 if f.geomType()=='CYLINDER':
  c=BRepAdaptor_Surface(f.wrapped).Cylinder();d=c.Axis().Direction();l=c.Location()
  if abs(d.Z())>.999 and abs(c.Radius()-1.4)<1e-6:
   row=[l.X(),l.Y()]
   if row not in mounts:mounts.append(row)
 if f.geomType()=='PLANE' and abs(b.zmin-8.5)<1e-6 and b.zlen<1e-6:pins.append([(b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2])
assert len(pins)==40 and len(mounts)==4
holes=[[r['x_mm'],r['y_mm']] for r in j4['pads'] if r['number']=='' and r['drill_mm']==[1.02,1.02]]
mp=[[r['x_mm'],r['y_mm']] for r in j4['pads'] if r['number']=='MP']
assert len(holes)==40 and len(mp)==4
# Axis mapping native KiCad STEP already flips board Y; both STEP systems Z-up.
header_tx=sum(p[0] for p in pins)/40-sum(p[0] for p in holes)/40
header_ty=sum(p[1] for p in pins)/40+sum(p[1] for p in holes)/40
e['host_board_faces']=large;e['host_mount_holes_mm']=mounts;e['host_header_tip_centers_mm']=pins;e['hat_mount_holes_mm']=mp;e['hat_pass_through_holes_mm']=holes
# Exported mask establishes the CAD HAT B.Mask surface; don't equate substrate z=0 to board surface.
mask_faces=[]
for i,f in enumerate(surfaces.Faces()):
 b=f.BoundingBox()
 if f.Area()>500:mask_faces.append(dict(face=i,type=f.geomType(),area_mm2=f.Area(),bbox_mm=box(f)))
e['hat_large_surface_faces']=mask_faces
# Current KiCad export: mask outer bound -0.085 (includes native export offsets).
mask_bottom=surfaces.BoundingBox().zmin
assert -.10 < mask_bottom < -.06, box(surfaces)
tz=4.0-mask_bottom
e['assumed_surface_gap_mm']=4.0;e['hat_native_mask_bottom_z_mm']=mask_bottom;e['native_to_radxa_translation_z_mm']=tz
e['c45_generic_dimensions_mm']=[c45.BoundingBox().xlen,c45.BoundingBox().ylen,c45.BoundingBox().zlen]
host_faces_with_boxes=[(f,box(f)) for f in host.Faces()]
e['placements']={}
for name,tx,ty in [('document_nominal',-70.9025,106.135),('header_grid_aligned',header_tx,header_ty)]:
 t=(tx,ty,tz);cc=c45.translate(t);bb=board.translate(t);bc=bottom.translate(t)
 row=dict(native_kicad_step_to_radxa_translation_mm=list(t),hat_pcb_xy_to_radxa=f'Xr=Xhat+({tx}); Yr=-Yhat+({ty})',c45_bbox_mm=box(cc),header_residuals_mm=[min(math.dist([x+tx,-y+ty],p) for p in pins) for x,y in holes],mount_residuals_mm=[min(math.dist([x+tx,-y+ty],p) for p in mounts) for x,y in mp])
 row['c45_to_host']=measure(cc,host);print(name,'c45',row['c45_to_host'],flush=True)
 # Supplier maximum-dimensional MLCC bounding envelope, NOT an exact replacement model.
 b=cc.BoundingBox(); envelope=cq.Workplane('XY').box(2.7,3.5,2.7).val().translate(((b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2,b.zmax-2.7/2))
 row['c45_max_dimension_envelope_to_host']=measure(envelope,host)
 row['c45_max_dimension_envelope_bbox_mm']=box(envelope)
 row['board_to_host']=measure(bb,host);print(name,'board',row['board_to_host'],flush=True)
 row['bottom_to_host']=measure(bc,host);print(name,'bottom',row['bottom_to_host'],flush=True)
 # Save aggregate evidence before detailed checks. Exact full-solid distance above is the global result.
 e['placements'][name]=row;pathlib.Path(a.output).write_text(json.dumps(e,indent=2))
 # Conservative 1mm broad-phase per FACE for detailed proximity, not per fused host solid.
 # A face excluded by these bounds cannot be within 1mm of this component.
 near=[]
 for i,s in enumerate(bc.Solids()):
  sb=box(s)
  local=[f for f,fb in host_faces_with_boxes if all(sb[k]-1 <= fb[k+1] and fb[k]-1 <= sb[k+1] for k in [0,2,4])]
  if not local:continue
  m=measure(s,cq.Compound.makeCompound(local),False)
  if m['minimum_distance_mm']<1.0:near.append(dict(solid_index=i,bbox_mm=sb,**m))
 row['bottom_solids_under_1mm']=near
 row['c45_gap_sensitivity']=[dict(surface_gap_mm=g,**measure(c45.translate((tx,ty,g-mask_bottom)),host)) for g in [3.5,3.84,4.0,4.5]]
 e['placements'][name]=row
 pathlib.Path(a.output).write_text(json.dumps(e,indent=2))
 if name=='header_grid_aligned':
  ass=cq.Assembly(name='PARTIAL_RADXA_HAT_REFERENCE_4MM_MASK_GAP');ass.add(host,name='official_Radxa',color=cq.Color('green'));ass.add(bb,name='HAT_substrate',color=cq.Color('blue'));ass.add(bc,name='available_bottom_models',color=cq.Color('gray'));ass.save(str(w/'partial_stack_header_aligned.step'))
e['source_unchanged_after_analysis']=sha(inputs['source_pcb'])==inputs['pcb_sha256']
pathlib.Path(a.output).write_text(json.dumps(e,indent=2));print('evidence',a.output,flush=True)
# OCP/VTK Windows wheels can crash during interpreter teardown after successful work.
# All required outputs are flushed before this deliberate clean exit; errors above still fail normally.
sys.stdout.flush();os._exit(0)
