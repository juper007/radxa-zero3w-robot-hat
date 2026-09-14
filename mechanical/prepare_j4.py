"""Native scratch-only exact J4 placement; acquired licensed model stays outside repo."""
import argparse,hashlib,json,os,pathlib,subprocess
import pcbnew
from evidence_contract import require, J4_MODEL_SHA256, J4_ROTATION, J4_OFFSET
if not __debug__:
 raise RuntimeError('optimized execution is unsupported for J4 preparation')
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--scratch',required=True);a=p.parse_args()
r=pathlib.Path(__file__).resolve().parents[1];w=pathlib.Path(a.scratch);w.mkdir(parents=True,exist_ok=True)
source=r/'hardware/kicad/radxa_zero3w_robot_hat.kicad_pcb';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();before=sha(source)
assert sha(a.model)=='d5503fca60b62f7d24dcaec78bbc2f76d75032de7a299e5beee15c5749f0aad5'
b=pcbnew.LoadBoard(str(source));f=b.FindFootprintByReference('J4');assert f.GetLayer()==pcbnew.B_Cu and abs(f.GetOrientationDegrees()+90)<1e-6
# Inspect the actual PCB model before constructing the separate candidate.
current=list(f.Models());require(len(current)==1, 'J4 current model inventory')
cm=current[0]
current_model=pathlib.Path(str(cm.m_Filename).replace('${KIPRJMOD}',str(source.parent))).resolve()
vector=lambda v:[v.x,v.y,v.z]
require(sha(current_model)==J4_MODEL_SHA256, 'J4 current model pin')
require(vector(cm.m_Rotation)==J4_ROTATION and vector(cm.m_Offset)==J4_OFFSET and vector(cm.m_Scale)==[1,1,1], 'J4 current model transform')
f.Models().clear();m=pcbnew.FP_3DMODEL();m.m_Filename=str(pathlib.Path(a.model).resolve());m.m_Rotation=pcbnew.VECTOR3D(-90,0,90);m.m_Offset=pcbnew.VECTOR3D(0,-4.19905533063427,0.302503373819);f.Add3DModel(m)
candidate=w/'j4-candidate.kicad_pcb';pcbnew.SaveBoard(str(candidate),b)
cmd=[os.environ['LOCALAPPDATA']+'/Programs/KiCad/10.0/bin/kicad-cli.exe','pcb','export','step','--force','--no-board-body','--component-filter','J4','--user-origin','0x0mm','-o',str(w/'j4-test.step'),str(candidate)]
x=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(w/'j4-export.log').write_text(x.stdout);print(x.stdout);x.check_returncode();assert sha(source)==before
(w/'j4-export-metadata.json').write_text(json.dumps(dict(command=cmd,source_pcb_sha256=before,model_sha256=sha(a.model),rotation_deg=[-90,0,90],offset_mm=[0,-4.19905533063427,.302503373819],native_step_sha256=sha(w/'j4-test.step'),source_unchanged=True),indent=2))
# Direct source export has its OWN binding, never the candidate's metadata.
import tempfile
with tempfile.TemporaryDirectory(prefix='.j4-current-',dir=w) as temporary:
 stage=pathlib.Path(temporary);step=stage/'j4-current.step'
 direct=[*cmd[:-2],str(step),str(source)]
 x=subprocess.run(direct,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
 (w/'j4-current-export.log').write_text(x.stdout);print(x.stdout);x.check_returncode()
 require(step.is_file() and step.stat().st_size>10000, 'J4 current export missing/empty')
 require(sha(source)==before and sha(current_model)==J4_MODEL_SHA256, 'J4 source/model changed during export')
 metadata=dict(command=direct,source_pcb=str(source),source_pcb_sha256=before,model_file=str(current_model),model_sha256=J4_MODEL_SHA256,rotation_deg=J4_ROTATION,offset_mm=J4_OFFSET,scale=[1,1,1],native_step_file='j4-current.step',native_step_sha256=sha(step),source_unchanged=True)
 manifest=stage/'j4-current-metadata.json';manifest.write_text(json.dumps(metadata,indent=2))
 os.replace(step,w/step.name);os.replace(manifest,w/manifest.name)
