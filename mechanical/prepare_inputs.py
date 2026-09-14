"""Run with KiCad bundled python. Read-only PCB inspection/native STEP export."""
import argparse, hashlib, json, os, pathlib, subprocess, urllib.request, zipfile
import pcbnew
from evidence_contract import acquire_official, OFFICIAL_URL
p=argparse.ArgumentParser();p.add_argument('--scratch',required=True);a=p.parse_args()
root=pathlib.Path(__file__).resolve().parents[1]; out=pathlib.Path(a.scratch);out.mkdir(parents=True,exist_ok=True)
pcb=root/'hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb'
kicad=pathlib.Path(os.environ['LOCALAPPDATA'])/'Programs/KiCad/10.0'
url=OFFICIAL_URL
acquire_official(out)
archive=out/'official-current.zip';host=out/'official_radxa.stp'
sha=lambda f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
b=pcbnew.LoadBoard(str(pcb)); rows=[]
for f in b.GetFootprints():
    rows.append(dict(ref=f.GetReference(),value=f.GetValue(),footprint=f.GetFPID().GetUniStringLibId(),x_mm=pcbnew.ToMM(f.GetPosition().x),y_mm=pcbnew.ToMM(f.GetPosition().y),rotation_deg=f.GetOrientationDegrees(),layer=f.GetLayerName(),dnp=f.IsDNP(),models=[dict(path=str(m.m_Filename),offset=[m.m_Offset.x,m.m_Offset.y,m.m_Offset.z],rotation=[m.m_Rotation.x,m.m_Rotation.y,m.m_Rotation.z],scale=[m.m_Scale.x,m.m_Scale.y,m.m_Scale.z]) for m in f.Models()],pads=[dict(number=p.GetNumber(),x_mm=pcbnew.ToMM(p.GetPosition().x),y_mm=pcbnew.ToMM(p.GetPosition().y),drill_mm=[pcbnew.ToMM(p.GetDrillSize().x),pcbnew.ToMM(p.GetDrillSize().y)]) for p in f.Pads()]))
data=dict(source_pcb=str(pcb),pcb_sha256=sha(pcb),git_head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),kicad_version=pcbnew.GetBuildVersion(),thickness_mm=pcbnew.ToMM(b.GetDesignSettings().GetBoardThickness()),source_url=url,zip_sha256=sha(archive),step_sha256=sha(host),footprints=rows)
cache=pathlib.Path(os.environ['LOCALAPPDATA'])/'Temp/radxa-zero3w-mech/extracted/radxa_zero_3w_3d.stp'
data['cache_sha256']=sha(cache) if cache.exists() else None; data['cache_matches_current']=data['cache_sha256']==data['step_sha256']
(out/'inputs.json').write_text(json.dumps(data,indent=2))
models=kicad/'share/kicad/3dmodels'
commands=[]
for name,options in [('c45',['--no-board-body','--component-filter','C45']),('board',['--board-only']),('surfaces',['--no-components','--include-pads','--include-soldermask']),('bottom',['--no-board-body','--component-filter',','.join(r['ref'] for r in rows if r['layer']=='B.Cu' and r['ref']!='J4' and not r['dnp'])])]:
    cmd=[str(kicad/'bin/kicad-cli.exe'),'pcb','export','step','--force','--user-origin','0x0mm','--define-var',f'KICAD9_3DMODEL_DIR={models}','--define-var',f'KICAD10_3DMODEL_DIR={models}',*options,'-o',str(out/(name+'.step')),str(pcb)]
    result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True); (out/(name+'-export.log')).write_text(result.stdout);commands.append(dict(command=cmd,exit_code=result.returncode)); print(name,result.returncode,result.stdout[-1800:]);result.check_returncode()
(out/'commands.json').write_text(json.dumps(commands,indent=2));print(json.dumps({k:v for k,v in data.items() if k!='footprints'},indent=2))
