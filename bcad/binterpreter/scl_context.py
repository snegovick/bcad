import os

from OCC.Core.AIS import AIS_ColoredShape, AIS_Line
from OCC.Core.Geom import Geom_Line, Geom_Point
from OCC.Core.Prs3d import Prs3d_LineAspect, Prs3d_Drawer, Prs3d_Projector
from OCC.Core.HLRBRep import HLRBRep_HLRToShape, HLRBRep_Algo
from OCC.Core.HLRAlgo import HLRAlgo_Projector
from OCC.Core.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec, gp_Pln, gp_Ax3
from OCC.Core.ChFi2d import ChFi2d_AnaFilletAlgo
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeCone, BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.TopoDS import topods, TopoDS_Compound, TopoDS_Solid
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_ALICEBLUE, Quantity_NOC_ANTIQUEWHITE, Quantity_NOC_BLACK, Quantity_NOC_MATRAGRAY, Quantity_NOC_YELLOW, Quantity_NOC_PERU
from OCC.Core.Aspect import Aspect_Grid
from OCC.Core.V3d import V3d_XposYnegZpos, V3d_XposYposZpos, V3d_XnegYposZpos, V3d_XnegYnegZpos, V3d_XposYposZneg, V3d_XnegYposZneg, V3d_XposYnegZneg, V3d_XnegYnegZneg
#from OCC.Display.SimpleGui import init_display
from OCC.Display.OCCViewer import rgb_color
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Extend.ShapeFactory import make_wire
from OCC.Extend.DataExchange import read_step_file_with_names_colors, read_stl_file

from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.XCAFDoc import (XCAFDoc_DocumentTool_ShapeTool,
                              XCAFDoc_DocumentTool_ColorTool)
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
from OCC.Core.TDF import TDF_LabelSequence, TDF_Label
from OCC.Core.TCollection import TCollection_ExtendedString
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.TopLoc import TopLoc_Location

from bcad.binterpreter.bgui import init_display
from bcad.binterpreter.colorname_map import colorname_map
from bcad.binterpreter.events import EVEnum, EventProcessor, ee, ep
from bcad.binterpreter.singleton import Singleton
from bcad.binterpreter.scl_shape import SCLShape, DISP_MODE_WIREFRAME
from bcad.binterpreter.scl_util import Noval, is_var_set

from logging import debug, info, warning, error, critical

import math

class ContextError(Exception):
    def __init__(self, preamble, fname, line):
        self.message = "%s in %s at line %i"%(preamble, fname, line)

    def __str__(self):
        return self.message

names = {
    "translate": 0,
    "rotate": 0,
    "color": 0,
    "cube": 0,
    "polygon": 0,
    "cylinder": 0,
    "linear_extrude": 0,
    "union": 0,
    "intersection": 0,
    "difference": 0,
    "projection": 0,
    "profile2": 0,
    "step": 0,
    "stl": 0,
    "part": 0,
    "extrusion": 0,
    "loft": 0,
    "unknown": 0,
}

def get_inc_name(prefix):
    if prefix not in names:
        n = "unk_"+prefix+str(names["unknown"])
        names["unknown"]+=1
    else:
        n = prefix+str(names[prefix])
        names[prefix]+=1
    return n

class SCLDisplay:
    def __init__(self):
        self.display = None
        self.start_display = None
        self.scl_init_display()

    def mk_colored_line(self, start, direction, color, linestyle, width):
        line = Geom_Line(start, direction)
        ais_line = AIS_Line(line)

        drawer = ais_line.Attributes()
        aspect = Prs3d_LineAspect(color, linestyle, width)
        drawer.SetLineAspect(aspect)
        ais_line.SetAttributes(drawer)
        return ais_line

    def axis(self):
        center = gp_Pnt(0,0,0)
        zd = gp_Dir(0,0,10000)
        self.display.Context.Display(self.mk_colored_line(center, zd, rgb_color(0,0,1), 0, 1.0), False)

        xd = gp_Dir(1,0,0)
        self.display.Context.Display(self.mk_colored_line(center, xd, rgb_color(1,0,0), 0, 1.0), False)

        yd = gp_Dir(0,1,0)
        self.display.Context.Display(self.mk_colored_line(center, yd, rgb_color(0,1,0), 0, 1.0), False)

    def perspective(self, event=None):
        self.display.SetPerspectiveProjection()
        self.display.FitAll()

    def orthographic(self, event=None):
        self.display.SetOrthographicProjection()
        self.display.FitAll()

    def top(self, event=None):
        self.display.View_Top()
        self.display.Context.UpdateCurrentViewer()

    def bottom(self, event=None):
        self.display.View_Bottom()
        self.display.Context.UpdateCurrentViewer()

    def left(self, event=None):
        self.display.View_Left()
        self.display.Context.UpdateCurrentViewer()

    def right(self, event=None):
        self.display.View_Right()
        self.display.Context.UpdateCurrentViewer()

    def front(self, event=None):
        self.display.View_Front()
        self.display.Context.UpdateCurrentViewer()

    def rear(self, event=None):
        self.display.View_Rear()
        self.display.Context.UpdateCurrentViewer()

    def rxp(self, event=None):
        self.display.View.Rotate(math.radians(15),0,0, True)
        self.display.Context.UpdateCurrentViewer()

    def rxn(self, event=None):
        self.display.View.Rotate(math.radians(-15),0,0, True)
        self.display.Context.UpdateCurrentViewer()

    def ryp(self, event=None):
        self.display.View.Rotate(0,math.radians(15),0, True)
        self.display.Context.UpdateCurrentViewer()

    def ryn(self, event=None):
        self.display.View.Rotate(0,math.radians(-15),0, True)
        self.display.Context.UpdateCurrentViewer()

    def rzp(self, event=None):
        self.display.View.Rotate(0,0,math.radians(15), True)
        self.display.Context.UpdateCurrentViewer()

    def rzn(self, event=None):
        self.display.View.Rotate(0,0,math.radians(-15), True)
        self.display.Context.UpdateCurrentViewer()

    def isometric1(self, event=None):
        self.display.View_Iso()
        self.display.FitAll()

    def isometric2(self, event=None):
        self.display.View.SetProj(V3d_XposYposZpos)
        self.display.FitAll()

    def isometric3(self, event=None):
        self.display.View.SetProj(V3d_XnegYposZpos)
        self.display.FitAll()

    def isometric4(self, event=None):
        self.display.View.SetProj(V3d_XnegYnegZpos)
        self.display.FitAll()

    def isometric5(self, event=None):
        self.display.View.SetProj(V3d_XposYposZneg)
        self.display.FitAll()

    def isometric6(self, event=None):
        self.display.View.SetProj(V3d_XnegYposZneg)
        self.display.FitAll()

    def isometric7(self, event=None):
        self.display.View.SetProj(V3d_XposYnegZneg)
        self.display.FitAll()

    def isometric8(self, event=None):
        self.display.View.SetProj(V3d_XnegYnegZneg)
        self.display.FitAll()

    def reset(self, event=None):
        #self.display.Context.CloseAllContexts()
        self.display.Context.RemoveAll(True)
        self.axis()
        self.display.Repaint()

    def periodic(self):
        ep.process()

    def scl_init_display(self):
        self.display, self.start_display = init_display(periodic_callback=self.periodic, period=1)
        self.display.SetRenderingParams(Method=0, RaytracingDepth=3, IsShadowEnabled=False, IsReflectionEnabled=False, IsAntialiasingEnabled=False, IsTransparentShadowEnabled=False, StereoMode=0, AnaglyphFilter=1, ToReverseStereo=False)


        # self.add_menu('View')
        # self.add_function_to_menu('View', self.top)
        # self.add_function_to_menu('View', self.bottom)
        # self.add_function_to_menu('View', self.left)
        # self.add_function_to_menu('View', self.right)
        # self.add_function_to_menu('View', self.front)
        # self.add_function_to_menu('View', self.rear)
        # self.add_function_to_menu('View', self.isometric1)
        # self.add_function_to_menu('View', self.isometric2)
        # self.add_function_to_menu('View', self.isometric3)
        # self.add_function_to_menu('View', self.isometric4)
        # self.add_function_to_menu('View', self.isometric5)
        # self.add_function_to_menu('View', self.isometric6)
        # self.add_function_to_menu('View', self.isometric7)
        # self.add_function_to_menu('View', self.isometric8)
        # self.add_function_to_menu('View', self.perspective)
        # self.add_function_to_menu('View', self.orthographic)
        # self.add_function_to_menu('View', self.reset)
        # self.add_function_to_menu('View', self.rxp) # positive x rotation
        # self.add_function_to_menu('View', self.rxn) # negative x rotation
        # self.add_function_to_menu('View', self.ryp)
        # self.add_function_to_menu('View', self.ryn)
        # self.add_function_to_menu('View', self.rzp)
        # self.add_function_to_menu('View', self.rzn)


        p = gp_Pnt(0., 0., 0.)
        d = gp_Dir(0., 0., 1.)
        a = gp_Ax3(p, d)

        self.display.View.SetBgGradientColors(Quantity_Color(Quantity_NOC_ALICEBLUE), Quantity_Color(Quantity_NOC_ALICEBLUE), 2, True)

        self.axis()

        self.display.Repaint()

class V2:
    def __init__(self, x, y):
        self.v = [x,y]

    def x(self):
        return self.v[0]

    def y(self):
        return self.v[1]

    def __repr__(self):
        return "<V2 (%f,%f)>"%(self.v[0], self.v[1])

class V3:
    def __init__(self, x, y, z):
        self.v = [x,y,z]

    def x(self):
        return self.v[0]

    def y(self):
        return self.v[1]

    def z(self):
        return self.v[2]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if (self.x() == other.x()) and (self.y() == other.y()) and (self.z() == other.z()):
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<V3 (%f,%f,%f)>"%(self.v[0], self.v[1], self.v[2])

class Line3:
    def __init__(self, sp, dp):
        self.sp = sp
        self.dp = dp
        self.edge = None

    def to_edge(self):
        if (self.edge == None):
            s = gp_Pnt(self.sp.x(), self.sp.y(), self.sp.z())
            e = gp_Pnt(self.dp.x(), self.dp.y(), self.dp.z())
            self.edge = BRepBuilderAPI_MakeEdge(s, e).Edge()
        return self.edge

    def __repr__(self):
        return "<Line (%s; %s)>"%(repr(self.sp), repr(self.dp))

class Fillet2:
    def __init__(self, radius=1.0):
        self.radius = radius
        self.edge = None
        self.l1 = None
        self.l2 = None

    def to_edge(self, l1, l2):
        if (self.edge == None):
            f = ChFi2d_AnaFilletAlgo()
            f.Init(l1.to_edge(), l2.to_edge(), gp_Pln())
            f.Perform(self.radius)
            self.edge = f.Result(l1.to_edge(), l2.to_edge())
            self.l1 = l1
            self.l2 = l2
        return self.edge

    def __repr__(self):
        return "<Fillet (%s;%s)>"%(repr(self.l1), repr(self.l2))

class SCLContext(object):
    def __init__(self, parent):
        self.parent = parent
        self.children = []
        self.name = None

    def set_name(self, name):
        self.name = name

    def add_child_context(self, ctx):
        self.children.append(ctx)

    def propagate_trsf(self, trsf):
        debug("Apply transform to %s: %s"%(self.name, type(self),))
        self.apply_trsf(trsf)
        for c in self.children:
            c.propagate_trsf(trsf)

    def propagate_color(self, color):
        debug("Apply color to %s: %s"%(self.name, type(self),))
        self.apply_color(color)
        for c in self.children:
            c.propagate_color(color)

    def propagate_display_mode(self, mode):
        debug("Apply mode to %s: %s"%(self.name, type(self),))
        self.apply_display_mode(mode)
        for c in self.children:
            c.propagate_display_mode(mode)

    def display(self, writer=None):
        debug("Display SCLContext")
        objects = []
        for c in self.children:
            objects.append(self.child.display(writer))
        objects = {'name': self.name, 'children': objects}
        debug("end SCLContext")
        return objects

    def start_display(self, writer=None):
        if (writer == None):
            if (self.parent == None):
                Singleton.sd.display.FitAll()
                Singleton.sd.start_display()

    def get_children(self):
        children = []
        for c in self.children:
            children.append(c)
            children.extend(c.get_children())
        return children

class SCLPart3(SCLContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.shape = None
        self.profile = None

    def set_shape(self, shape):
        self.shape = shape

    def apply_color(self, color):
        if self.shape != None:
            self.shape.color(color)

    def apply_trsf(self, trsf):
        if self.shape != None:
            self.shape.transform(trsf)

    def apply_display_mode(self, mode):
        if self.shape != None:
            self.shape.display_mode = mode

    def rotate(self, x=0.0, y=0.0, z=0.0):
        trsf = gp_Trsf()
        if (x!=0.0):
            axx = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(1., 0., 0.))
            a_trsf1 = gp_Trsf()
            a_trsf1.SetRotation(axx, math.radians(x))
            #trsf = trsf*a_trsf1
            trsf = a_trsf1*trsf

        if (y!=0.0):
            axy = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0., 1., 0.))
            a_trsf2 = gp_Trsf()
            a_trsf2.SetRotation(axy, math.radians(y))
            #trsf = trsf*a_trsf2
            trsf = a_trsf2*trsf

        if (z!=0.0):
            axz = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0., 0., 1.))
            a_trsf3 = gp_Trsf()
            a_trsf3.SetRotation(axz, math.radians(z))
            #trsf = trsf*a_trsf3
            trsf = a_trsf3*trsf

        for c in self.children:
            c.propagate_trsf(trsf)

    def display_wireframe(self):
        self.display_mode = DISP_MODE_WIREFRAME
        for c in self.children:
            c.propagate_display_mode(self.display_mode)

    def translate(self, x=0.0, y=0.0, z=0.0):
        v = gp_Vec(x, y, z)
        a_trsf = gp_Trsf()
        a_trsf.SetTranslation(v)
        for c in self.children:
            c.propagate_trsf(a_trsf)

    def mirror(self, x=0.0, y=0.0, z=0.0):
        debug("mirror: %f, %f, %f"%(x,y,z))
        if (x==0 and y==0 and z==0):
            warning("Warning: no axis to mirror")
            return
        trsf = gp_Trsf()

        d = gp_Dir(x, y, z)
        p = gp_Pnt(0,0,0)
        trsf.SetMirror(gp_Ax2(p, d))
        for c in self.children:
            c.propagate_trsf(trsf)

    def color(self, v):
        for c in self.children:
            c.propagate_color(v)

    def cube(self, xyz, center=False):
        cube_shape = BRepPrimAPI_MakeBox(xyz.x(), xyz.y(), xyz.z()).Shape()

        scls = SCLShape(cube_shape)
        if (center):
            debug("center cube")
            trsf = gp_Trsf()
            trsf.SetTranslation(gp_Vec(-xyz.x()/2.0, -xyz.y()/2.0, -xyz.z()/2.0))
            scls.transform(trsf)
        sclp = SCLPart3(self)
        sclp.set_shape(scls)
        name = get_inc_name("cube")
        sclp.set_name(name)
        debug("Creating cube %s"%(name,))
        self.add_child_context(sclp)

    def polygon(self, points, paths, fname, line):
        p = SCLProfile2(self)
        if paths == []:
            paths = [i for i in range(len(points))]
        for e, pth in enumerate(paths):
            start = int(paths[e-1])
            end = int(paths[e])
            if ((start>=len(points)) or (start<0)):
                raise ContextError("Point #%i start index (%i) is out of range"%(e, start), fname, line)
            if ((end>=len(points)) or (end<0)):
                raise ContextError("Point #%i end index (%i) is out of range"%(e, end), fname, line)

            ps = points[start]
            pe = points[end]
            if (len(ps)<2):
                raise ContextError("Element with index #%i is not a point: need at array of 2 elements, got %s"%(start, str(ps)), fname, line)
            if (len(pe)<2):
                raise ContextError("Element with index #%i is not a point: need at array of 2 elements, got %s"%(end, str(pe)), fname, line)
            v2s = V3(ps[0], ps[1], 0)
            v2e = V3(pe[0], pe[1], 0)
            p.line(v2s, v2e)
        self.add_child_context(p)
        p.set_name(get_inc_name("polygon"))
        self.profile = p

    def get_face(self):
        if (self.profile != None):
            return self.profile.get_face()
        warning("Part contains no profile")
        return None

    def get_wire(self):
        if (self.profile != None):
            return self.profile.get_wire()
        warning("Part contains no profile")
        return None

    def cylinder(self, r, r1, r2, d, d1, d2, h, center=False):
        nr1 = None
        nr2 = None
        nh = None
        if (not is_var_set(d)) and is_var_set(r):
            nr1 = r
            nr2 = r
        elif is_var_set(d) and (not is_var_set(r)):
            nr1 = d/2.0
            nr2 = d/2.0
        elif is_var_set(d) and is_var_set(r):
            nr1 = d/2.0
            nr2 = d/2.0
        elif (not is_var_set(d)) and (not is_var_set(r)) and (is_var_set(r1) and is_var_set(r2)):
            nr1 = r1
            nr2 = r2
        elif (not is_var_set(d)) and (not is_var_set(r)) and (is_var_set(d1) and is_var_set(d2)):
            nr1 = d1/2.0
            nr2 = d2/2.0
        else:
            nr1 = 0.5
            nr2 = 0.5

        nh = 1.0
        if is_var_set(h):
            nh = h

        ax = gp_Ax2(gp_Pnt(0,0,0), gp_Dir(0,0,1))
        s = None
        if nr1==nr2:
            s = BRepPrimAPI_MakeCylinder(ax, nr1, nh).Shape()
        else:
            s = BRepPrimAPI_MakeCone(ax, nr1, nr2, nh).Shape()
        scls = SCLShape(s)
        if (center):
            debug("center cylinder")
            trsf = gp_Trsf()
            trsf.SetTranslation(gp_Vec(0, 0, -h/2.0))
            scls.transform(trsf)
        sclp = SCLPart3(self)
        sclp.set_shape(scls)
        name = get_inc_name("cylinder")
        sclp.set_name(name)
        debug("Creating cylinder %s"%(name,))
        self.add_child_context(sclp)

    def read_step(self, filename):
        """ Returns list of tuples (topods_shape, label, color)
        Use OCAF.
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError("%s not found." % filename)
        debug("Loading %s"%(filename,))
        # the list:
        output_shapes = {}

        # create an handle to a document
        doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))

        # Get root assembly
        shape_tool = XCAFDoc_DocumentTool_ShapeTool(doc.Main())
        color_tool = XCAFDoc_DocumentTool_ColorTool(doc.Main())
        #layer_tool = XCAFDoc_DocumentTool_LayerTool(doc.Main())
        #mat_tool = XCAFDoc_DocumentTool_MaterialTool(doc.Main())

        step_reader = STEPCAFControl_Reader()
        step_reader.SetColorMode(True)
        step_reader.SetLayerMode(True)
        step_reader.SetNameMode(True)
        step_reader.SetMatMode(True)
        step_reader.SetGDTMode(True)

        debug("Read step file")
        status = step_reader.ReadFile(filename)
        if status == IFSelect_RetDone:
            step_reader.Transfer(doc)
        debug("Done reading")

        locs = []

        def _get_sub_shapes(lab, loc):
            #global cnt, lvl
            #cnt += 1
            #print("\n[%d] level %d, handling LABEL %s\n" % (cnt, lvl, _get_label_name(lab)))
            #print()
            #print(lab.DumpToString())
            #print()
            #print("Is Assembly    :", shape_tool.IsAssembly(lab))
            #print("Is Free        :", shape_tool.IsFree(lab))
            #print("Is Shape       :", shape_tool.IsShape(lab))
            #print("Is Compound    :", shape_tool.IsCompound(lab))
            #print("Is Component   :", shape_tool.IsComponent(lab))
            #print("Is SimpleShape :", shape_tool.IsSimpleShape(lab))
            #print("Is Reference   :", shape_tool.IsReference(lab))

            #users = TDF_LabelSequence()
            #users_cnt = shape_tool.GetUsers(lab, users)
            #print("Nr Users       :", users_cnt)

            l_subss = TDF_LabelSequence()
            shape_tool.GetSubShapes(lab, l_subss)
            #print("Nb subshapes   :", l_subss.Length())
            l_comps = TDF_LabelSequence()
            shape_tool.GetComponents(lab, l_comps)
            #print("Nb components  :", l_comps.Length())
            #print()
            name = lab.GetLabelName()
            debug("Name : %s"%(name,))

            if shape_tool.IsAssembly(lab):
                l_c = TDF_LabelSequence()
                shape_tool.GetComponents(lab, l_c)
                for i in range(l_c.Length()):
                    label = l_c.Value(i+1)
                    if shape_tool.IsReference(label):
                        #print("\n########  reference label :", label)
                        label_reference = TDF_Label()
                        shape_tool.GetReferredShape(label, label_reference)
                        loc = shape_tool.GetLocation(label)
                        #print("    loc          :", loc)
                        #trans = loc.Transformation()
                        #print("    tran form    :", trans.Form())
                        #rot = trans.GetRotation()
                        #print("    rotation     :", rot)
                        #print("    X            :", rot.X())
                        #print("    Y            :", rot.Y())
                        #print("    Z            :", rot.Z())
                        #print("    W            :", rot.W())
                        #tran = trans.TranslationPart()
                        #print("    translation  :", tran)
                        #print("    X            :", tran.X())
                        #print("    Y            :", tran.Y())
                        #print("    Z            :", tran.Z())

                        locs.append(loc)
                        #print(">>>>")
                        #lvl += 1
                        _get_sub_shapes(label_reference, loc)
                        #lvl -= 1
                        #print("<<<<")
                        locs.pop()

            elif shape_tool.IsSimpleShape(lab):
                #print("\n########  simpleshape label :", lab)
                shape = shape_tool.GetShape(lab)
                #print("    all ass locs   :", locs)

                loc = TopLoc_Location()
                for l in locs:
                    #print("    take loc       :", l)
                    loc = loc.Multiplied(l)

                #trans = loc.Transformation()
                #print("    FINAL loc    :")
                #print("    tran form    :", trans.Form())
                #rot = trans.GetRotation()
                #print("    rotation     :", rot)
                #print("    X            :", rot.X())
                #print("    Y            :", rot.Y())
                #print("    Z            :", rot.Z())
                #print("    W            :", rot.W())
                #tran = trans.TranslationPart()
                #print("    translation  :", tran)
                #print("    X            :", tran.X())
                #print("    Y            :", tran.Y())
                #print("    Z            :", tran.Z())
                c = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)  # default color
                colorSet = False
                if (color_tool.GetInstanceColor(shape, 0, c) or
                        color_tool.GetInstanceColor(shape, 1, c) or
                        color_tool.GetInstanceColor(shape, 2, c)):
                    color_tool.SetInstanceColor(shape, 0, c)
                    color_tool.SetInstanceColor(shape, 1, c)
                    color_tool.SetInstanceColor(shape, 2, c)
                    colorSet = True
                    n = c.Name(c.Red(), c.Green(), c.Blue())
                    debug('    instance color Name & RGB: %s %s %s %s %s'%(str(c), str(n), str(c.Red()), str(c.Green()), str(c.Blue())))

                if not colorSet:
                    if (color_tool.GetColor(lab, 0, c) or
                            color_tool.GetColor(lab, 1, c) or
                            color_tool.GetColor(lab, 2, c)):

                        color_tool.SetInstanceColor(shape, 0, c)
                        color_tool.SetInstanceColor(shape, 1, c)
                        color_tool.SetInstanceColor(shape, 2, c)

                        n = c.Name(c.Red(), c.Green(), c.Blue())
                        debug('    shape color Name & RGB: %s %s %s %s %s'%(str(c), str(n), str(c.Red()), str(c.Green()), str(c.Blue())))

                shape_disp = BRepBuilderAPI_Transform(shape, loc.Transformation()).Shape()
                if not shape_disp in output_shapes:
                    output_shapes[shape_disp] = [name, lab.GetLabelName(), c]
                for i in range(l_subss.Length()):
                    lab_subs = l_subss.Value(i+1)
                    #print("\n########  simpleshape subshape label :", lab)
                    shape_sub = shape_tool.GetShape(lab_subs)

                    c = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)  # default color
                    colorSet = False
                    if (color_tool.GetInstanceColor(shape_sub, 0, c) or
                            color_tool.GetInstanceColor(shape_sub, 1, c) or
                            color_tool.GetInstanceColor(shape_sub, 2, c)):
                        color_tool.SetInstanceColor(shape_sub, 0, c)
                        color_tool.SetInstanceColor(shape_sub, 1, c)
                        color_tool.SetInstanceColor(shape_sub, 2, c)
                        colorSet = True
                        n = c.Name(c.Red(), c.Green(), c.Blue())
                        debug('    instance color Name & RGB: %s %s %s %s %s'%(str(c), str(n), str(c.Red()), str(c.Green()), str(c.Blue())))

                    if not colorSet:
                        if (color_tool.GetColor(lab_subs, 0, c) or
                                color_tool.GetColor(lab_subs, 1, c) or
                                color_tool.GetColor(lab_subs, 2, c)):
                            color_tool.SetInstanceColor(shape, 0, c)
                            color_tool.SetInstanceColor(shape, 1, c)
                            color_tool.SetInstanceColor(shape, 2, c)

                            n = c.Name(c.Red(), c.Green(), c.Blue())
                            debug('    shape color Name & RGB: %s %s %s %s %s'%(str(c), str(n), str(c.Red()), str(c.Green()), str(c.Blue())))
                    shape_to_disp = BRepBuilderAPI_Transform(shape_sub, loc.Transformation()).Shape()
                    # position the subshape to display
                    if not shape_to_disp in output_shapes:
                        output_shapes[shape_to_disp] = [name, lab_subs.GetLabelName(), c]


        def _get_shapes():
            debug("Get shapes")
            labels = TDF_LabelSequence()
            shape_tool.GetFreeShapes(labels)
            #global cnt
            #cnt += 1

            debug("Number of shapes at root : %s"%(str(labels.Length(),)))
            for i in range(labels.Length()):
                root_item = labels.Value(i+1)
                debug("Get sub shapes")
                _get_sub_shapes(root_item, None)
            debug("Get shapes done")
        _get_shapes()
        return output_shapes


    def import_step(self, filename):
        shapes_labels_colors = self.read_step(filename)
        prev_name = None
        part = None
        for shpt_lbl_color in shapes_labels_colors:
            name, label, c = shapes_labels_colors[shpt_lbl_color]
            debug("name: %s, label: %s, shpt_lbl_color: %s"%(str(name), str(label), str(shpt_lbl_color),))
            # if (type(shpt_lbl_color) != TopoDS_Solid):
            #     debug("skip")
            #     continue
            current_part = None
            if prev_name != name:
                prev_name = name
                scls = SCLShape(shpt_lbl_color)
                scls.color([c.Red(), c.Green(), c.Blue()])
                part = SCLPart3(self)
                part.set_shape(scls)
                #name = get_inc_name(name)
                part.set_name(name)
                current_part = part
            else:
                scls = SCLShape(shpt_lbl_color)
                scls.color([c.Red(), c.Green(), c.Blue()])
                sclp = SCLPart3(part)
                sclp.set_shape(scls)
                #name = get_inc_name(name)
                sclp.set_name(name)
                current_part = sclp
            debug("Creating step %s"%(name,))
            self.add_child_context(current_part)

    def import_stl(self, filename):
        stl_shp = read_stl_file(filename)
        scls = SCLShape(stl_shp)
        sclp = SCLPart3(self)
        sclp.set_shape(scls)
        name = get_inc_name("stl")
        sclp.set_name(name)
        debug("Creating stl %s"%(name,))
        self.add_child_context(sclp)

    def display(self, writer=None):
        debug("Display SCLPart3 %s"%(self.name,))
        #if self.display_mode == DISP_MODE_HLR:
            #Singleton.sd.display.SetModeHLR()
        #else:
            #Singleton.sd.display.SetModeShaded()
        objects = []
        for c in self.children:
            objects.append(c.display(writer))
        objects = {'name': self.name, 'children': objects}

        if self.shape != None:
            self.shape.display(writer)

        debug("end SCLPart3")
        return objects

    def start_display(self, writer=None):
        if (writer == None):
            if (self.parent == None):
                Singleton.sd.display.FitAll()
                Singleton.sd.start_display()

class SCLProfile2(SCLContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.edges = []
        self.wire = None
        self.trsf = gp_Trsf()
        self.face = None

    def line(self, p2_src, p2_dest):
        self.push_element(Line3(p2_src, p2_dest))

    def fillet(self, radius):
        self.push_element(Fillet2(radius))

    def push_element(self, e):
        self.edges.append(e)

    # def rotate(self, x=0.0, y=0.0, z=0.0):
    #     if (x!=0.0):
    #         axx = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(1., 0., 0.))
    #         a_trsf1 = gp_Trsf()
    #         a_trsf1.SetRotation(axx, math.radians(x))
    #         self.trsf = self.trsf*a_trsf1

    #     if (y!=0.0):
    #         axy = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0., 1., 0.))
    #         a_trsf2 = gp_Trsf()
    #         a_trsf2.SetRotation(axy, math.radians(y))
    #         self.trsf = self.trsf*a_trsf2

    #     if (z!=0.0):
    #         axz = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0., 0., 1.))
    #         a_trsf3 = gp_Trsf()
    #         a_trsf3.SetRotation(axz, math.radians(z))
    #         self.trsf = self.trsf*a_trsf3

    # def mirror(self, x=0.0, y=0.0, z=0.0):
    #     if (x==0 and y== 0 and z==0):
    #         warning("Warning: no axis to mirror")
    #         return
    #     trsf = gp_Trsf()

    #     d = gp_Dir(x, y, z)
    #     p = gp_Pnt()
    #     trsf.SetMirror(gp_Ax1(p, d))
    #     self.trsf = self.trsf*trsf

    def transform(self, trsf):
        self.wire = topods.Wire(BRepBuilderAPI_Transform(self.get_wire(), trsf, True).Shape())

    def apply_trsf(self, trsf):
        self.transform(trsf)

    def get_wire(self):
        if (self.wire == None):
            occ_edges = []
            for i, e in enumerate(self.edges):
                o = "Element %i/%i: "%(i, len(self.edges))
                if (isinstance(e, Line3)):
                    occ_edges.append(e.to_edge())
                elif (isinstance(e, Fillet2)):
                    if ((len(self.edges))<=(i+1)):
                        error("Not enough elements for fillet")
                        exit(0)
                    else:
                        occ_edges.append(e.to_edge(self.edges[i-1], self.edges[i+1]))
                o+=repr(e)
                debug(o)
            if occ_edges == []:
                return None
            self.wire = make_wire(occ_edges)
            trsf_wire = BRepBuilderAPI_Transform(self.wire, self.trsf)
            trsf_shape = trsf_wire.Shape()
            self.wire = topods.Wire(trsf_shape)
            self.face = None
        return self.wire

    def get_face(self):
        if (self.face == None):
            self.face = BRepBuilderAPI_MakeFace(self.get_wire())
        return self.face

    def display(self, writer=None):
        debug("Display SCLProfile2")
        w = self.get_wire()
        objects = {'name': self.name, 'children': None}
        if (w != None):
            Singleton.sd.display.DisplayShape(w, writer)
        debug("end SCLProfile2")
        return objects

class SCLExtrude(SCLContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.shape = None

    def apply_trsf(self, trsf):
        if self.shape != None:
            self.shape.transform(trsf)

    def linear_extrude(self, height=1.0):
        faces = []
        for c in self.children:
            debug("Adding face")
            f = c.get_face()
            faces.append(f)

        self.children = []

        for f in faces:
            prism_vec = gp_Vec(0, 0, height)
            shape = BRepPrimAPI_MakePrism(f.Face(), prism_vec).Shape()
            scls = SCLShape(shape)
            sclp = SCLPart3(self)
            sclp.set_shape(scls)
            name = get_inc_name("extrusion")
            sclp.set_name(name)
            debug("Creating extrusion %s"%(name,))
            self.add_child_context(sclp)

    def display(self, writer=None):
        debug("Display SCLExtrude")
        debug("Children: %s"%(repr(self.children),))
        objects = []
        for c in self.children:
            objects.append(c.display(writer))
        objects = {'name': self.name, 'children': objects}
        
        if self.shape != None:
            self.shape.display(writer)
        debug("end SCLExtrude")
        return objects

def collect_wires(this):
    wires = []
    for c in this.children:
        if not isinstance(c, SCLProfile2):
            collected_wires = collect_wires(c)
            wires+=collected_wires
        else:
            w = c.get_wire()
            if w!=None:
                wires.append(w)
    return wires

class SCLLoft(SCLContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.shape = None

    def apply_trsf(self, trsf):
        if self.shape != None:
            self.shape.transform(trsf)

    def loft(self, solid=True, ruled=True, precision=0.000001):
        wires = collect_wires(self)

        self.children = []

        generator = BRepOffsetAPI_ThruSections(solid, ruled, precision)

        for w in wires:
            debug("wire: %s"%(str(w),))
            generator.AddWire(w)
        generator.Build()

        shape = generator.Shape()
        scls = SCLShape(shape)
        sclp = SCLPart3(self)
        sclp.set_shape(scls)
        name = get_inc_name("loft")
        sclp.set_name(name)
        debug("Creating loft %s"%(name,))
        self.add_child_context(sclp)

    def display(self, writer=None):
        debug("Display SCLLoft")
        debug("Children: %s"%(repr(self.children),))
        objects = []
        for c in self.children:
            objects.append(c.display(writer))
        objects = {'name': self.name, 'children': objects}

        if self.shape != None:
            self.shape.display(writer)
        debug("end SCLLoft")
        return objects

class SCLUnion(SCLPart3):
    def __init__(self, parent):
        super().__init__(parent)

    def union(self):
        children = self.get_children()
        shapes = []
        debug("children: %s"%(children,))
        for c in children:
            if c.shape != None:
                shapes.append(c.shape)
        u = None
        if len(shapes)>0:
            u = shapes[0].get_shape()
            for s in shapes[1:]:
                u = BRepAlgoAPI_Fuse(u, s.get_shape()).Shape()
        self.shape = SCLShape(u)
        self.children = []

    def display(self, writer=None):
        debug("Display SCLUnion")
        objects = {'name': self.name, 'children': None}
        if self.shape != None:
            self.shape.display(writer)
        debug("end SCLUnion")
        return objects

class SCLIntersection(SCLPart3):
    def __init__(self, parent):
        super().__init__(parent)

    def intersection(self):
        children = self.get_children()
        shapes = []
        debug("children: %s"%(children,))
        for c in children:
            if c.shape != None:
                shapes.append(c.shape)
        u = None
        if len(shapes)>0:
            u = shapes[0].get_shape()
            for s in shapes[1:]:
                u = BRepAlgoAPI_Common(u, s.get_shape()).Shape()
        self.shape = SCLShape(u)
        self.children = []

    def display(self, writer=None):
        debug("Display SCLIntersection")
        if self.shape != None:
            self.shape.display(writer)
        objects = {'name': self.name, 'children': None}
        debug("end SCLIntersection")
        return objects

class SCLDifference(SCLPart3):
    def __init__(self, parent):
        super().__init__(parent)

    def difference(self):
        children = self.get_children()
        shapes = []
        debug("children: %s"%(children,))
        for c in children:
            if c.shape != None:
                shapes.append(c.shape)
        u = None
        f = None
        if len(shapes)>1:
            f = shapes[0].get_shape()
            for s in shapes[1:]:
                f = BRepAlgoAPI_Cut(f, s.get_shape()).Shape()
        self.shape = SCLShape(f)
        self.shape.set_shape_color(shapes[0].get_shape_color())
        self.children = []

    def display(self, writer=None):
        debug("Display SCLDifference")
        if self.shape != None:
            self.shape.display(writer)
        objects = {'name': self.name, 'children': None}
        debug("end SCLDifference")
        return objects

class SCLProjection(SCLPart3):
    def __init__(self, parent):
        super().__init__(parent)

    def projector(self, trsf):
        p = Prs3d_Projector(False, 0.0, 0,0,0, 0,0,-1, 0,0,1).Projector()
        return p

    def projection(self):
        children = self.get_children()
        shapes = []
        debug("children: %s"%(children,))
        for c in children:
            if c.shape != None:
                shapes.append(c.shape.get_shape())
        self.hlr_project(shapes)

    def hlr_project(self, shapes):
        hlralgo = HLRBRep_Algo()
        if len(shapes)>0:
            for s in shapes:
                hlralgo.Add(s)
            self.children = []
            trsf = gp_Trsf()
            p = HLRAlgo_Projector(gp_Ax2(gp_Pnt(), gp_Dir(0, 0, 1)))
            hlralgo.Projector(p)
            hlralgo.Update()
            hlralgo.Hide()
            hlrtoshape = HLRBRep_HLRToShape(hlralgo)
            vcompound = hlrtoshape.VCompound()
            voutline = hlrtoshape.OutLineVCompound()
            rg1linevcompound = hlrtoshape.Rg1LineVCompound()
            rgnlinevcompound = hlrtoshape.RgNLineVCompound()
            isolinevcompound = hlrtoshape.IsoLineVCompound()
            hcompound = hlrtoshape.HCompound()
            houtline = hlrtoshape.OutLineHCompound()
            rg1linehcompound = hlrtoshape.Rg1LineHCompound()
            rgnlinehcompound = hlrtoshape.RgNLineHCompound()
            isolinehcompound = hlrtoshape.IsoLineHCompound()
            debug("vcompound: %s"%(str(vcompound),))
            debug("voutline: %s"%(str(voutline),))
            debug("rg1linevcompound: %s"%(str(rg1linevcompound),))
            debug("rgnlinevcompound: %s"%(str(rgnlinevcompound),))
            debug("isolinevcompound: %s"%(str(isolinevcompound),))
            debug("hcompound: %s"%(str(hcompound),))
            debug("houtline: %s"%(str(houtline),))
            debug("rg1linehcompound: %s"%(str(rg1linehcompound),))
            debug("rgnlinehcompound: %s"%(str(rgnlinehcompound),))
            debug("isolinehcompound: %s"%(str(isolinehcompound),))
            name = get_inc_name("projection")
            if (vcompound != None):
                sclp = SCLPart3(self)
                scls = SCLShape(vcompound)
                scls.set_linestyle("main_projection")
                sclp.set_shape(scls)
                sclp.set_name(name+'vcompound')
                self.add_child_context(sclp)
            if (voutline != None):
                sclp = SCLPart3(self)
                scls = SCLShape(voutline)
                scls.set_linestyle("main_projection")
                sclp.set_shape(scls)
                sclp.set_name(name+'voutline')
                self.add_child_context(sclp)
            if (rg1linevcompound != None):
                sclp = SCLPart3(self)
                scls = SCLShape(rg1linevcompound)
                scls.set_linestyle("main_projection")
                sclp.set_shape(scls)
                sclp.set_name(name+'rg1linevcompound')
                self.add_child_context(sclp)
            if (rgnlinevcompound != None):
                sclp = SCLPart3(self)
                scls = SCLShape(rgnlinevcompound)
                scls.set_linestyle("main_projection")
                sclp.set_shape(scls)
                sclp.set_name(name+'rgnlinecompound')
                self.add_child_context(sclp)
            if (isolinevcompound != None):
                sclp = SCLPart3(self)
                scls = SCLShape(isolinevcompound)
                scls.set_linestyle("main_projection")
                sclp.set_shape(scls)
                sclp.set_name(name+'isolinevcompound')
                self.add_child_context(sclp)
            if (hcompound != None):
                sclp = SCLPart3(self)
                scls = SCLShape(hcompound)
                scls.set_linestyle("hidden")
                scls.set_hidden(True)
                sclp.set_shape(scls)
                sclp.set_name(name+'hcompound')
                self.add_child_context(sclp)
            if (houtline != None):
                sclp = SCLPart3(self)
                scls = SCLShape(houtline)
                scls.set_linestyle("hidden")
                scls.set_hidden(True)
                sclp.set_shape(scls)
                sclp.set_name(name+'houtline')
                self.add_child_context(sclp)
            if (rg1linehcompound != None):
                sclp = SCLPart3(self)
                scls = SCLShape(rg1linehcompound)
                scls.set_linestyle("hidden")
                scls.set_hidden(True)
                sclp.set_shape(scls)
                sclp.set_name(name+'rg1linehcompound')
                self.add_child_context(sclp)
            if (rgnlinehcompound != None):
                sclp = SCLPart3(self)
                scls = SCLShape(rgnlinehcompound)
                scls.set_linestyle("hidden")
                scls.set_hidden(True)
                sclp.set_shape(scls)
                sclp.set_name(name+'rgnlinehcompound')
                self.add_child_context(sclp)
            if (isolinehcompound != None):
                sclp = SCLPart3(self)
                scls = SCLShape(isolinehcompound)
                scls.set_linestyle("hidden")
                scls.set_hidden(True)
                sclp.set_shape(scls)
                sclp.set_name(name+'isolinehcompound')
                self.add_child_context(sclp)


    def display(self, writer=None):
        debug("Display SCLProjection")
        objects = []
        for c in self.children:
            objects.append(c.display(writer))
        if self.shape != None:
            self.shape.display(writer)
        objects = {'name': self.name, 'children': objects}
        debug("end SCLProjection")
        return objects
