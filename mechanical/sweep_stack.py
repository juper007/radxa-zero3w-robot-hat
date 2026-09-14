"""Source-bound sensitivity study. CAD only, never assembly approval.

Import safe: CAD imports, source verification and writes occur only on request.
"""
import math
from pathlib import Path
from evidence_contract import require, sha, verify_official, verify_j4

EXPORT_NAMES = frozenset(('official_radxa.stp', 'board.step', 'bottom.step', 'surfaces.step', 'c45.step'))


def verify_export_inventory(scratch, records):
    require(isinstance(records, dict) and set(records) == EXPORT_NAMES, 'CAD export inventory')
    for name, record in records.items():
        require(record['sha256'] == sha(Path(scratch)/name), f'export hash: {name}')



def stack_datums(gap, mask_bottom, mask_top, socket_lower, host_top, plastic_top, pin_tip):
    """Signed axial geometry, NOT contact wipe or insertion acceptance."""
    if not all(math.isfinite(v) for v in (gap, mask_bottom, mask_top, socket_lower, host_top, plastic_top, pin_tip)):
        raise ValueError('nonfinite datum')
    if gap <= 0 or mask_top <= mask_bottom or not host_top < plastic_top < pin_tip or socket_lower >= mask_bottom:
        raise ValueError('invalid gap or ordered datums')
    tz = host_top + gap - mask_bottom
    lower = socket_lower + tz
    return dict(translation_z_mm=tz, socket_lower_face_z_mm=lower,
                body_lower_face_minus_host_plastic_top_mm=lower-plastic_top,
                pin_tip_above_hat_bottom_mm=pin_tip-(mask_bottom+tz),
                pin_tip_above_hat_top_mm=pin_tip-(mask_top+tz),
                axial_entry_past_socket_lower_face_mm=pin_tip-lower)


EVT_TARGET_GAP_MM = 9.5
PUBLISHED_ENTRY_RANGE_MM = (1.78, 3.43)
GAPS = (4., 6.2, 6.5, 7., 8., 9., EVT_TARGET_GAP_MM, 10.)
POPULATED_BOTTOM = frozenset('C1 C14 C15 C16 C17 C18 C2 C22 C26 C27 C28 C29 C3 C30 C31 C32 C33 C34 C35 C36 C37 C38 C39 C4 C44 C45 C5 C6 C7 C8 C9 D1 D4 FB1 FB2 FB3 J4 Q2 R1 R18 R2 R20 R21 R29 R3 R31 R32 R33 R34 R35 R38 R39 R4 R40 R5 R6 R7 R8 TH1 U1 U10 U2 U5 U6 U7 U8 Y1'.split())
DNP_BOTTOM = frozenset('R11 R10 C25 U4 R41 R17'.split())


def evt_stack_decision():
    """Selected representative build basis; physical qualification stays open."""
    return dict(surface_gap_mm=EVT_TARGET_GAP_MM, fastener='M2',
                host_header_basis='official Radxa standard 2x20 geometry',
                published_entry_range_mm=list(PUBLISHED_ENTRY_RANGE_MM),
                physical_validation_required=True, fabrication_ready=False)


def preflight(scratch, evidence_dir=None):
    """Read-only checks before importing CAD. Never invoke writing legacy scripts.

    Existing final-source evidence binds the current PCB and exact STEP bytes.
    No equivalence file, old-source hash or current-source override is accepted.
    """
    import json
    from evidence_contract import verify_render
    w = Path(scratch).resolve()
    r = Path(evidence_dir or Path(__file__).parent).resolve()
    read = lambda path: json.loads(path.read_text())
    i, c, j = read(w/'inputs.json'), read(r/'cad_evidence.json'), read(r/'j4_evidence.json')
    pcb = r.parent/'hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb'
    require(Path(i['source_pcb']).resolve() == pcb.resolve(), 'source PCB path')
    require(i['pcb_sha256'] == c['inputs']['pcb_sha256'] == j['source_pcb_sha256'] == sha(pcb), 'current source PCB hash')
    require(c['inputs'] == {k:v for k,v in i.items() if k != 'footprints'}, 'CAD inputs binding')
    require(c['source_unchanged_after_analysis'] is True, 'CAD source changed')
    verify_export_inventory(w, c['exports'])
    verify_official(w, i, c['inputs'])
    jm = verify_j4(w, i, j)
    require(j['analyzed_native_step_sha256'] == sha(w/'j4-current.step'), 'J4 analyzed export hash')
    require(Path(j['analyzed_native_step']).resolve() == (w/'j4-current.step').resolve(), 'J4 analyzed direct export')
    bottom = [f for f in i['footprints'] if f['layer'] == 'B.Cu']
    pop = [f['ref'] for f in bottom if not f['dnp']]
    dnp = [f['ref'] for f in bottom if f['dnp']]
    require(len(pop) == len(POPULATED_BOTTOM) and set(pop) == POPULATED_BOTTOM, 'populated bottom inventory')
    require(len(dnp) == len(DNP_BOTTOM) and set(dnp) == DNP_BOTTOM, 'DNP bottom inventory')
    require(c['exports']['bottom.step']['solids'] == len(POPULATED_BOTTOM-{'J4','Y1'}), 'represented bottom inventory')
    commands = read(w/'commands.json')
    require(len(commands) == 4, 'native export command inventory')
    seen = set()
    for record in commands:
        cmd = record['command']
        name = Path(cmd[cmd.index('-o')+1]).name
        require(name not in seen, 'duplicate native export command')
        seen.add(name)
        require(record['exit_code'] == 0 and Path(cmd[-1]).resolve() == pcb.resolve(), 'native export source/exit')
        require(cmd[cmd.index('--user-origin')+1] == '0x0mm', 'native export origin')
        if name == 'bottom.step':
            refs = cmd[cmd.index('--component-filter')+1].split(',')
            require(len(refs) == len(POPULATED_BOTTOM-{'J4'}) and set(refs) == POPULATED_BOTTOM-{'J4'}, 'bottom export filter inventory')
    require(seen == EXPORT_NAMES-{'official_radxa.stp'}, 'native export command names')
    verify_render(w, r, read(r/'render_evidence.json'))
    require(len(c['host_header_tip_centers_mm']) == 40 and len(j['lead_seating_faces']) == 40, 'existing pin/lead evidence inventory')
    require(set(j['gaps']) == {'4.0','6.2','6.5'} and j['gaps']['4.0']['intersection_below_host_header_top_mm3'] > 400, 'existing J4 diagnostics')
    files = [pcb, Path(jm['model_file']), Path(__file__), r/'evidence_contract.py',
             *[w/n for n in sorted(EXPORT_NAMES)], w/'j4-current.step',
             w/'official-current.zip', w/'inputs.json', w/'commands.json',
             w/'j4-current-metadata.json', *[r/n for n in ('cad_evidence.json','j4_evidence.json','render_evidence.json','stack_4mm.png','stack_4mm_header_side.png')]]
    binding = dict(source_pcb_sha256=i['pcb_sha256'],
                   files=[dict(path=str(p), sha256=sha(p)) for p in files],
                   populated_bottom_refs=sorted(pop), excluded_dnp_refs=sorted(dnp),
                   represented_bottom_refs=sorted(POPULATED_BOTTOM-{'J4','Y1'}),
                   missing_bottom_refs=['Y1'], exact_j4_separate=True,
                   existing_evidence_verified_before_cad=True)
    return i, c, binding


def run_sweep(scratch):
    """Real complete BRep distances/Booleans; return only after all checks."""
    i, previous, binding = preflight(scratch)
    print('Preflight passed: current PCB, exact inventories and export hashes', flush=True)
    import cadquery as cq
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    w = Path(scratch)

    def bbox(s):
        b = s.BoundingBox()
        return [b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax]

    def measure(a, b):
        d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
        d.Perform()
        require(d.IsDone() and d.NbSolution() > 0, 'BRep distance failed')
        u, v = d.PointOnShape1(1), d.PointOnShape2(1)
        common = a.intersect(b)
        volume = common.Volume()
        require(math.isfinite(volume) and volume >= -1e-8, 'invalid Boolean volume')
        return dict(minimum_distance_mm=d.Value(), intersection_volume_mm3=volume,
                    point_a_mm=[u.X(),u.Y(),u.Z()], point_b_mm=[v.X(),v.Y(),v.Z()])

    shapes = {n: cq.importers.importStep(str(w/n)).val() for n in sorted(EXPORT_NAMES|{'j4-current.step'})}
    geometry = {n: dict(bbox_mm=bbox(s), solids=len(s.Solids())) for n,s in shapes.items()}
    for name in EXPORT_NAMES:
        require(geometry[name]['solids'] == previous['exports'][name]['solids'], f'actual solid inventory: {name}')
        require(max(abs(a-b) for a,b in zip(geometry[name]['bbox_mm'], previous['exports'][name]['bbox_mm'])) < 1e-6, f'actual bounds: {name}')
    host, j4 = shapes['official_radxa.stp'], shapes['j4-current.step']
    pins, plastic, boardplanes = [], [], []
    for index, f in enumerate(host.Faces()):
        b = f.BoundingBox()
        if f.geomType() != 'PLANE':
            continue
        plane = BRepAdaptor_Surface(f.wrapped).Plane()
        if abs(plane.Axis().Direction().Z()) < .999999:
            continue
        z = plane.Location().Z()
        row = dict(face=index, plane_z_mm=z, bbox_mm=bbox(f), area_mm2=f.Area())
        if abs(z-8.5) < 1e-6 and b.zlen < 1e-6:
            row.update(center_xy_mm=[(b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2], width_x_mm=b.xlen, width_y_mm=b.ylen)
            pins.append(row)
        if abs(z-2.5) < 1e-6 and b.ymin > 24 and b.ymax < 30 and b.xlen > 40:
            plastic.append(row)
        if f.Area() > 500 and abs(z) < 1e-6:
            boardplanes.append(row)
    require(len(pins) == 40 and plastic and boardplanes, 'measured host datum faces')
    pin_z = sum(p['plane_z_mm'] for p in pins)/len(pins)
    plastic_z = sum(p['plane_z_mm'] for p in plastic)/len(plastic)
    host_z = sum(p['plane_z_mm'] for p in boardplanes)/len(boardplanes)
    require(all(p['width_x_mm'] > 0 and p['width_y_mm'] > 0 for p in pins), 'tip face cross-sections')
    fp = next(f for f in i['footprints'] if f['ref'] == 'J4')
    holes = [p for p in fp['pads'] if p['number'] == '' and p['drill_mm'] == [1.02,1.02]]
    require(len(holes) == 40, 'J4 passage inventory')
    cx = sum(p['center_xy_mm'][0] for p in pins)/40
    cy = sum(p['center_xy_mm'][1] for p in pins)/40
    tx = cx-sum(p['x_mm'] for p in holes)/40
    ty = cy+sum(p['y_mm'] for p in holes)/40
    residuals = [min(math.dist([p['x_mm']+tx, -p['y_mm']+ty], t['center_xy_mm']) for t in pins) for p in holes]
    require(max(residuals) < 1e-6, 'header grid alignment')
    sb = shapes['surfaces.step'].BoundingBox()
    mask_bottom, mask_top = sb.zmin, sb.zmax
    socket_lower = j4.BoundingBox().zmin
    lower_faces = [dict(face=k, bbox_mm=bbox(f), area_mm2=f.Area()) for k,f in enumerate(j4.Faces())
                   if f.geomType() == 'PLANE' and f.BoundingBox().zlen < 1e-6 and abs(f.BoundingBox().zmin-socket_lower) < 1e-6]
    require(lower_faces and -.10 < mask_bottom < -.06 and .90 < mask_top < .95, 'measured HAT/socket datums')
    window = cq.Workplane('XY').box(50.8,5.08,2.499).val().translate((cx,cy,1.2495))
    low_host = host.intersect(window)
    cb = shapes['c45.step'].BoundingBox()
    envelope = cq.Workplane('XY').box(2.7,3.5,2.7).val().translate(((cb.xmin+cb.xmax)/2,(cb.ymin+cb.ymax)/2,cb.zmax-1.35))
    result = dict(schema_version=1, fabrication_ready=False, measurement_type='CAD only, not physical',
                  evt_stack_decision=evt_stack_decision(),
                  cadquery=cq.__version__, source_binding=binding, geometry=geometry,
                  datums=dict(host_pin_tip_faces=pins, host_header_plastic_top_faces=plastic,
                    host_board_top_faces=boardplanes, host_pin_tip_z_mm=pin_z, host_plastic_top_z_mm=plastic_z,
                    host_board_top_z_mm=host_z, hat_mask_bottom_native_z_mm=mask_bottom,
                    hat_mask_top_native_z_mm=mask_top, socket_lower_native_z_mm=socket_lower,
                    socket_lower_faces=lower_faces, translation_xy_mm=[tx,ty], header_grid_residuals_mm=residuals),
                  diagnostic_window=dict(bbox_mm=bbox(window), description='Existing low host-header-region Boolean selection only; not a substitute connector model'),
                  c45_envelope=dict(dimensions_xyz_mm=[2.7,3.5,2.7], native_bbox_mm=bbox(envelope), description='Maximum-material bounding envelope at measured C45 seating plane, not exact supplier CAD'),
                  gaps=[], limitations=[
                    '9.5mm is the representative EVT target, not production assembly approval; fabrication_ready is false',
                    'Y1 missing underside model; top WAGO, other top bodies, cables, spacers and enclosure not reviewed',
                    'Official fused host includes the nominal standard 2x20 male-header geometry used as the EVT design basis',
                    'J4 complete intersection includes intended pin/contact regions, not a body-only collision metric',
                    'Axial entry is pin tip minus socket lower face, NOT wipe/contact acceptance or mating specification',
                    'Exact solder, board bow, seating, manufacturing and insertion tolerances remain open',
                    'Generic underside models and maximum-material C45 envelope do not prove physical clearance',
                    'Pin-tip face width is the imported tip shape, not a physical shaft-size measurement',
                    'Nominal 6.2mm body separation is below supplier general body-height tolerance; not a robust fit',
                    'No supplier insertion-depth limits applied: exact orientation/part applicability remains unresolved',
                    'Mounting-hole residuals and pin numbering require independent review',
                    'Licensed raw J4 model is kept in local scratch; no redistribution'])
    for gap in GAPS:
        datums = stack_datums(gap,mask_bottom,mask_top,socket_lower,host_z,plastic_z,pin_z)
        t = (tx,ty,datums['translation_z_mm'])
        placed = j4.translate(t)
        row = dict(surface_gap_mm=gap, fabrication_ready=False, axial_geometry=datums,
                   j4_bbox_mm=bbox(placed),
                   bottom_to_complete_host=measure(shapes['bottom.step'].translate(t),host),
                   c45_to_complete_host=measure(shapes['c45.step'].translate(t),host),
                   c45_max_material_envelope_to_host=measure(envelope.translate(t),host),
                   substrate_to_complete_host=measure(shapes['board.step'].translate(t),host),
                   j4_to_complete_host_including_contact_regions=measure(placed,host),
                   j4_low_header_region_intersection_mm3=placed.intersect(low_host).Volume())
        require(row['bottom_to_complete_host']['intersection_volume_mm3'] < 1e-8, 'unexpected bottom collision')
        if gap == 4.:
            require(row['j4_low_header_region_intersection_mm3'] > 400, '4mm collision regression')
            require(abs(row['bottom_to_complete_host']['minimum_distance_mm']-.005) < 1e-6, '4mm bottom distance regression')
            require(abs(row['c45_max_material_envelope_to_host']['minimum_distance_mm']-.465) < 1e-6, '4mm envelope distance regression')
        else:
            require(row['j4_low_header_region_intersection_mm3'] < 1e-8, 'unexpected low-header body intersection')
        result['gaps'].append(row)
        print('gap', gap, 'bottom',row['bottom_to_complete_host'], 'J4 low',row['j4_low_header_region_intersection_mm3'], flush=True)
    require(tuple(r['surface_gap_mm'] for r in result['gaps']) == GAPS, 'sweep completeness')
    # Bind exact bytes before AND after lengthy CAD; never bless a stale in-flight snapshot.
    for record in binding['files']:
        require(sha(record['path']) == record['sha256'], f'source/export changed during sweep: {record["path"]}')
    result['source_binding']['unchanged_after_sweep'] = True
    return result


def publish_evidence(payload, output):
    """Publish complete evidence atomically without replacing any destination.

    Hard-link creation is the no-clobber operation on Windows and POSIX.
    Filesystems without hard-link support fail closed; never fall back to rename.
    """
    import os
    import tempfile
    output = Path(output)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=output.parent, suffix='.tmp', delete=False) as stream:
            temp = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temp, output)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def main():
    import argparse
    import json
    import os
    import sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch', required=True)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('stack_sweep.json'))
    args = parser.parse_args()
    require(not args.output.exists(), 'refusing to overwrite existing evidence; select a NEW --output')
    result = run_sweep(args.scratch)
    payload = json.dumps(result, indent=2, allow_nan=False)+'\n'
    # Stage and publish only after the entire sweep succeeds.
    publish_evidence(payload, args.output)
    print('Published complete sweep:', args.output, flush=True)
    sys.stdout.flush()
    sys.stderr.flush()
    # Successful-end-only OCP Windows teardown workaround; all failures propagate.
    if os.name == 'nt':
        os._exit(0)


if __name__ == '__main__':
    main()
