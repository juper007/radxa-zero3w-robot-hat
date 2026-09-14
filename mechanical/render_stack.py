"""Render real tessellated CAD solids, not approximate drawing. Integrated view only."""
import argparse,pathlib,os,sys,json,hashlib
import cadquery as cq
import vtk
from evidence_contract import RENDER_TRANSLATION, sha, verify_official, publish_render, require
p=argparse.ArgumentParser();p.add_argument('--scratch',required=True);a=p.parse_args();w=pathlib.Path(a.scratch);out=pathlib.Path(__file__).parent
verify_official(w)
r=vtk.vtkRenderer();r.SetBackground(.045,.06,.09)
t=RENDER_TRANSLATION
items=[('official_radxa.stp',(0,0,0),(.25,.64,.38),1),('board.step',t,(.2,.48,1),.38),('bottom.step',t,(.7,.7,.72),1),('j4-current.step',t,(1,.45,.15),1),('c45.step',t,(1,.15,.25),1)]
metadata=[]
source_hashes={name:sha(w/name) for name,_,_,_ in items}
for name,tr,color,alpha in items:
 s=cq.importers.importStep(str(w/name)).val().translate(tr);vertices,triangles=s.tessellate(.06,.12)
 pts=vtk.vtkPoints()
 for v in vertices:pts.InsertNextPoint(v.x,v.y,v.z)
 cells=vtk.vtkCellArray()
 for tri in triangles:
  cells.InsertNextCell(3)
  for i in tri:cells.InsertCellPoint(i)
 poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells);mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly);actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*color);actor.GetProperty().SetOpacity(alpha);r.AddActor(actor)
 metadata.append(dict(file=name,sha256=source_hashes[name],translation_mm=tr,vertices=len(vertices),triangles=len(triangles)))
text=vtk.vtkTextActor();text.SetInput('PARTIAL CAD STACK | 4.0 mm assumed surface gap\nBlue: HAT substrate | Orange: exact J4 | Green: official Radxa | Red: C45\nJ4 interferes with host header. NOT assembly approved. No cables/spacers/WAGO bodies.');text.SetPosition(24,24);text.GetTextProperty().SetFontSize(19);text.GetTextProperty().SetColor(1,1,1);r.AddActor2D(text)
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.AddRenderer(r);window.SetSize(1600,1000);window.SetMultiSamples(4)
cam=r.GetActiveCamera();cam.SetPosition(88,83,48);cam.SetFocalPoint(32,15,1.5);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(29);r.ResetCameraClippingRange()
def render_image(path, view):
 if view == 1:
  cam.SetPosition(32,100,9);cam.SetFocalPoint(32,15,1.5);cam.SetParallelScale(19);r.ResetCameraClippingRange()
 window.Render();image=vtk.vtkWindowToImageFilter();image.SetInput(window);image.Update()
 writer=vtk.vtkPNGWriter();errors=[];writer.AddObserver('ErrorEvent',lambda *args:errors.append('VTK PNG writer error'))
 writer.SetFileName(str(path));writer.SetInputConnection(image.GetOutputPort());writer.Write()
 require(not errors and writer.GetErrorCode()==0, 'VTK PNG writer failed')
publish_render(w,out,dict(kind='OpenCascade tessellation with VTK rendering; real imported STEP surfaces',sources=metadata,assumed_gap_mm=4.0),render_image)
print(out/'stack_4mm.png',flush=True);window.Finalize();sys.stdout.flush();os._exit(0)
