"""Exact J4 CAD placement and interference checks; licensed model/export remain in scratch."""
import argparse,pathlib,json,hashlib,sys,os
import cadquery as cq
from evidence_contract import verify_j4, verify_official
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
p=argparse.ArgumentParser();p.add_argument('--scratch',required=True);a=p.parse_args();w=pathlib.Path(a.scratch);out=pathlib.Path(__file__).parent/'j4_evidence.json'
def bbox(s):
 b=s.BoundingBox();return [b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax]
def measure(a,b):
 d=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped);d.Perform();assert d.IsDone();return dict(distance_mm=d.Value(),intersection_volume_mm3=a.intersect(b).Volume())
e=verify_j4(w,json.loads((w/'inputs.json').read_text()));verify_official(w)
j4_path=w/'j4-current.step'
j=cq.importers.importStep(str(j4_path)).val();h=cq.importers.importStep(str(w/'official_radxa.stp')).val();board=cq.importers.importStep(str(w/'board.step')).val()
e.update(native_bbox_mm=bbox(j),cadquery=cq.__version__,measurement_type='CAD not physical',peg_centers_native_mm=[],lead_seating_faces=[])
e['analyzed_native_step']=str(j4_path);e['analyzed_native_step_sha256']=hashlib.sha256(j4_path.read_bytes()).hexdigest()
for i,f in enumerate(j.Faces()):
 b=f.BoundingBox()
 if f.geomType()=='CYLINDER':
  c=BRepAdaptor_Surface(f.wrapped).Cylinder();l=c.Location()
  if abs(c.Radius()-.79375)<1e-6:
   point=[l.X(),l.Y()]
   if not any(abs(x[0]-point[0])<1e-6 for x in e['peg_centers_native_mm']):e['peg_centers_native_mm'].append(point)
 if f.geomType()=='PLANE' and b.zlen<1e-6 and abs(b.zmin+.12)<1e-6:e['lead_seating_faces'].append(dict(i=i,bbox_mm=bbox(f),area_mm2=f.Area()))
assert len(e['peg_centers_native_mm'])==2 and len(e['lead_seating_faces'])==40
for actual,expected in zip(sorted(e['peg_centers_native_mm']),[[80.5375,-79.64],[126.2575,-79.64]]):assert max(abs(x-y) for x,y in zip(actual,expected))<1e-6
# Match lead seating face centroids to actual outward SMD pads, not to NPTH passages.
inp=json.loads((w/'inputs.json').read_text());pads=[x for r in inp['footprints'] if r['ref']=='J4' for x in r['pads'] if x['number'].isdigit()]
import math
e['lead_face_to_nearest_pad_center_distances_mm']=[min(math.dist([(r['bbox_mm'][0]+r['bbox_mm'][1])/2,(r['bbox_mm'][2]+r['bbox_mm'][3])/2],[p['x_mm'],-p['y_mm']]) for p in pads) for r in e['lead_seating_faces']]
e['j4_to_hat_substrate']=measure(j,board);out.write_text(json.dumps(e,indent=2));print('J4 against HAT',e['j4_to_hat_substrate'],flush=True)
# Header center alignment independently recovered from 40 host tip faces.
pins=[]
for f in h.Faces():
 b=f.BoundingBox()
 if f.geomType()=='PLANE' and abs(b.zmin-8.5)<1e-6 and b.zlen<1e-6:pins.append([(b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2])
assert len(pins)==40
tx=sum(p[0] for p in pins)/40-103.3975;ty=sum(p[1] for p in pins)/40+79.64
e['translation_xy_mm']=[tx,ty];e['gaps']={}
# Window strictly inside host plastic header envelope, excluding metal pins' potential contact zones.
# This is a diagnostic region, not an approximate connector replacement model.
window=cq.Workplane('XY').box(50.8,5.08,2.499).val().translate((32.450028,26.67508,1.2495))
hplastic=h.intersect(window)
for gap in [4.0,6.2,6.5]:
 placed=j.translate((tx,ty,gap+.085));row=dict(bbox_mm=bbox(placed),to_complete_host=measure(placed,h),intersection_below_host_header_top_mm3=placed.intersect(hplastic).Volume())
 e['gaps'][str(gap)]=row;out.write_text(json.dumps(e,indent=2));print('gap',gap,row,flush=True)
 if gap==4.0:
  ass=cq.Assembly(name='LICENSED_PARTIAL_STACK_COLLISION_4MM');ass.add(h,name='host',color=cq.Color('green'));ass.add(board.translate((tx,ty,gap+.085)),name='HAT_substrate',color=cq.Color('blue'));ass.add(placed,name='exact_J4',color=cq.Color('orange'));ass.save(str(w/'LICENSED_partial_stack_J4_4mm.step'))
e['limitations']=['Host male-header exact MPN and real solder/insertion tolerances unresolved','Pin-1/contact numbering not encoded by geometric lead placement alone','Large plastic interference is not permitted electrical contact; small contact overlaps require separate interpretation','No first-article verification; no assembly approval','Native lead Z=-0.12 is KiCad placement convention, not measured solder height','J4 STEP and integrated scratch assembly are licensed; no repository redistribution']
out.write_text(json.dumps(e,indent=2));print(out,flush=True);sys.stdout.flush();os._exit(0)
