"""Validate evidence completeness and source binding, NOT fabrication readiness."""
import argparse,hashlib,json,math,pathlib,struct
from evidence_contract import require, verify_official, verify_render, verify_j4
if not __debug__:
 raise RuntimeError('optimized execution is unsupported for evidence verification')
p=argparse.ArgumentParser();p.add_argument('--scratch',required=True);a=p.parse_args();w=pathlib.Path(a.scratch);r=pathlib.Path(__file__).parent
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=load(r/'cad_evidence.json')
require(isinstance(c.get('exports'), dict) and set(c['exports']) == {'official_radxa.stp','c45.step','board.step','bottom.step','surfaces.step'}, 'CAD export inventory')
j=load(r/'j4_evidence.json');v=load(r/'render_evidence.json');i=load(w/'inputs.json')
verify_official(w, i, c['inputs'])
verify_j4(w, i, j)
assert c['source_unchanged_after_analysis'];assert c['inputs']['pcb_sha256']==sha(pathlib.Path(i['source_pcb']))==j['source_pcb_sha256']==i['pcb_sha256']
assert len(c['host_header_tip_centers_mm'])==40;assert len(c['host_mount_holes_mm'])==4
assert set(c['placements'])=={'document_nominal','header_grid_aligned'}
assert len(j['lead_seating_faces'])==40;assert len(j['peg_centers_native_mm'])==2
assert j['analyzed_native_step'].endswith('j4-current.step');assert j['analyzed_native_step_sha256']==sha(w/'j4-current.step')
assert set(j['gaps'])=={'4.0','6.2','6.5'}
assert j['gaps']['4.0']['intersection_below_host_header_top_mm3']>400
assert c['exports']['bottom.step']['solids']==65
for name,x in c['exports'].items():assert x['sha256']==sha(w/name)
images=verify_render(w, r, v)
row=c['placements']['header_grid_aligned'];assert math.isclose(row['c45_to_host']['minimum_distance_mm'],.665,abs_tol=1e-6);assert math.isclose(row['c45_max_dimension_envelope_to_host']['minimum_distance_mm'],.465,abs_tol=1e-6)
assert math.isclose(row['bottom_to_host']['minimum_distance_mm'],.005,abs_tol=1e-6)
assert row['board_to_host']['intersection_volume_mm3']<1e-8
bottom=[f for f in i['footprints'] if f['layer']=='B.Cu'];pop=[f for f in bottom if not f['dnp']];assert len(bottom)==73 and len(pop)==67
refs=[];tx,ty,_=row['native_kicad_step_to_radxa_translation_mm']
for b in row['bottom_solids_under_1mm']:
 bb=b['bbox_mm'];center=[(bb[0]+bb[1])/2-tx,ty-(bb[2]+bb[3])/2];distance,ref=min((math.dist(center,[f['x_mm'],f['y_mm']]),f['ref']) for f in pop);assert distance<1e-6
 refs.append(dict(ref=ref,minimum_distance_mm=b['minimum_distance_mm']))
assert len(refs)==12 and min(refs,key=lambda r:r['minimum_distance_mm'])['ref']=='C7'
model=next(f for f in i['footprints'] if f['ref']=='J4')['models'];assert len(model)==1 and model[0]['path']=='${KIPRJMOD}/models-local/REF-182665-01.step';assert model[0]['rotation']==[-90,0,90]

result=dict(evidence_complete=True,fabrication_ready=False,measurement_type='CAD only, not physical',source_pcb_sha256=i['pcb_sha256'],checked_populated_bottom_refs=67,represented_bottom_excluding_j4=65,missing_bottom_model='Y1',exact_j4_separate=True,closest_bottom_refs=sorted(refs,key=lambda r:r['minimum_distance_mm']),images=images)
(r/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
