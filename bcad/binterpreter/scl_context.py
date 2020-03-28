from OCC.Core.AIS import AIS_ColoredShape, AIS_Line
from OCC.Core.Geom import Geom_Line, Geom_Point
from OCC.Core.Prs3d import Prs3d_LineAspect, Prs3d_Drawer, Prs3d_Projector
from OCC.Core.HLRBRep import HLRBRep_HLRToShape, HLRBRep_Algo
from OCC.Core.HLRAlgo import HLRAlgo_Projector
from OCC.Core.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec, gp_Pln, gp_Ax3
from OCC.Core.ChFi2d import ChFi2d_AnaFilletAlgo
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform, BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeCone, BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from OCC.Core.TopoDS import topods, TopoDS_Compound, TopoDS_Solid
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_ALICEBLUE, Quantity_NOC_ANTIQUEWHITE, Quantity_NOC_BLACK, Quantity_NOC_MATRAGRAY, Quantity_NOC_YELLOW, Quantity_NOC_PERU
from OCC.Core.Aspect import Aspect_Grid
#from OCC.Display.SimpleGui import init_display
from OCC.Display.OCCViewer import rgb_color
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Extend.ShapeFactory import make_wire
from OCC.Extend.DataExchange import read_step_file_with_names_colors, read_stl_file

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
        self.add_menu = None
        self.add_function_to_menu = None
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
        self.display.FitAll()

    def bottom(self, event=None):
        self.display.View_Bottom()
        self.display.FitAll()

    def left(self, event=None):
        self.display.View_Left()
        self.display.FitAll()

    def right(self, event=None):
        self.display.View_Right()
        self.display.FitAll()

    def front(self, event=None):
        self.display.View_Front()
        self.display.FitAll()

    def rear(self, event=None):
        self.display.View_Rear()
        self.display.FitAll()

    def isometric(self, event=None):
        self.display.View_Iso()
        self.display.FitAll()

    def reset(self, event=None):
        #self.display.Context.CloseAllContexts()
        self.display.Context.RemoveAll(True)
        self.axis()
        self.display.Repaint()

    def periodic(self):
        ep.process()

    def scl_init_display(self):
        self.display, self.start_display, self.add_menu, self.add_function_to_menu = init_display(size='fullscreen', periodic_callback=self.periodic, period=1)

        self.add_menu('View')
        self.add_function_to_menu('View', self.top)
        self.add_function_to_menu('View', self.bottom)
        self.add_function_to_menu('View', self.left)
        self.add_function_to_menu('View', self.right)
        self.add_function_to_menu('View', self.front)
        self.add_function_to_menu('View', self.rear)
        self.add_function_to_menu('View', self.isometric)
        self.add_function_to_menu('View', self.perspective)
        self.add_function_to_menu('View', self.orthographic)
        self.add_function_to_menu('View', self.reset)


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
        for c in self.children:
            c = self.child.display(writer)
        if (writer == None):
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

    def import_step(self, filename):
        shapes_labels_colors = read_step_file_with_names_colors(filename)
        for shpt_lbl_color in shapes_labels_colors:
            label, c = shapes_labels_colors[shpt_lbl_color]
            debug("shpt_lbl_color: %s"%(str(shpt_lbl_color),))
            if (type(shpt_lbl_color) != TopoDS_Solid):
                debug("skip")
                continue
            scls = SCLShape(shpt_lbl_color)
            scls.color([c.Red(), c.Green(), c.Blue()])
            sclp = SCLPart3(self)
            sclp.set_shape(scls)
            name = get_inc_name("step")
            sclp.set_name(name)
            debug("Creating step %s"%(name,))
            self.add_child_context(sclp)

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
        debug("Display SCLPart3")
        #if self.display_mode == DISP_MODE_HLR:
            #Singleton.sd.display.SetModeHLR()
        #else:
            #Singleton.sd.display.SetModeShaded()
        for c in self.children:
            c.display(writer)

        if self.shape != None:
            self.shape.display(writer)

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

    def rotate(self, x=0.0, y=0.0, z=0.0):
        if (x!=0.0):
            axx = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(1., 0., 0.))
            a_trsf1 = gp_Trsf()
            a_trsf1.SetRotation(axx, math.radians(x))
            self.trsf = self.trsf*a_trsf1

        if (y!=0.0):
            axy = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0., 1., 0.))
            a_trsf2 = gp_Trsf()
            a_trsf2.SetRotation(axy, math.radians(y))
            self.trsf = self.trsf*a_trsf2

        if (z!=0.0):
            axz = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0., 0., 1.))
            a_trsf3 = gp_Trsf()
            a_trsf3.SetRotation(axz, math.radians(z))
            self.trsf = self.trsf*a_trsf3

    def mirror(self, x=0.0, y=0.0, z=0.0):
        if (x==0 and y== 0 and z==0):
            warning("Warning: no axis to mirror")
            return
        trsf = gp_Trsf()

        d = gp_Dir(x, y, z)
        p = gp_Pnt()
        trsf.SetMirror(gp_Ax1(p, d))
        self.trsf = self.trsf*trsf

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
        return self.wire

    def get_face(self):
        if (self.face == None):
            self.face = BRepBuilderAPI_MakeFace(self.get_wire())
        return self.face

    def display(self, writer=None):
        debug("Display SCLProfile2")
        w = self.get_wire()
        if (w != None):
            Singleton.sd.display.DisplayShape(w, writer)

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
        for c in self.children:
            c.display(writer)

        if self.shape != None:
            self.shape.display(writer)

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
        if self.shape != None:
            self.shape.display(writer)

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
        debug("Display SCLUnion")
        if self.shape != None:
            self.shape.display(writer)

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
        for c in self.children:
            c.display(writer)
        if self.shape != None:
            self.shape.display(writer)
