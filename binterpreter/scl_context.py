from OCC.Core.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec, gp_Pln, gp_Ax3
from OCC.Core.ChFi2d import ChFi2d_AnaFilletAlgo
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform, BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox
from OCC.Extend.ShapeFactory import make_wire
from OCC.Display.SimpleGui import init_display
from OCC.Core.TopoDS import topods, TopoDS_Compound
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_ALICEBLUE, Quantity_NOC_ANTIQUEWHITE, Quantity_NOC_BLACK
from OCC.Core.Aspect import Aspect_Grid

from logging import debug, info, warning, error, critical

import math

display = None
start_display = None
add_menu = None
add_functionto_menu = None

names = {
    "translate": 0,
    "cube": 0,
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

def scl_init_display():
    global display
    global start_display
    global add_menu
    global add_functionto_menu
    display, start_display, add_menu, add_functionto_menu = init_display()
    p = gp_Pnt(0., 0., 0.)
    d = gp_Dir(0., 0., 1.)
    a = gp_Ax3(p, d)

    display.GetViewer().SetPrivilegedPlane(a)
    display.GetViewer().SetRectangularGridValues(0, 0, 1, 1, 0)
    display.GetViewer().SetRectangularGridGraphicValues(100, 100, 0)
    display.GetViewer().Grid().SetColors(Quantity_Color(Quantity_NOC_BLACK), Quantity_Color(Quantity_NOC_BLACK))

    display.GetViewer().ActivateGrid(0, 0)
    display.View.SetBgGradientColors(Quantity_Color(Quantity_NOC_ANTIQUEWHITE), Quantity_Color(Quantity_NOC_ANTIQUEWHITE), 2, True)
    display.Repaint()

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

    def display(self):
        debug("Display SCLContext")
        for c in self.children:
            c = self.child.display()
        display.FitAll()
        start_display()

class SCLShape(object):
    def __init__(self, shape):
        self.trsf = gp_Trsf()
        self.shape = shape

    def transform(self, trsf):
        self.trsf = self.trsf*trsf

    def transform_shape(self):
        self.shape = BRepBuilderAPI_Transform(self.shape, self.trsf, True).Shape()

    def display(self):
        self.transform_shape()
        display.DisplayShape(self.shape)

class SCLPart3(SCLContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.shape = None
    
    def set_shape(self, shape):
        self.shape = shape

    def apply_trsf(self, trsf):
        if self.shape != None:
            self.shape.transform(trsf)

    def rotate(self, x=0.0, y=0.0, z=0.0):
        trsf = gp_Trsf()
        if (x!=0.0):
            axx = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(1., 0., 0.))
            a_trsf1 = gp_Trsf()
            a_trsf1.SetRotation(axx, x)
            trsf = trsf*a_trsf1

        if (y!=0.0):
            axy = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0., 1., 0.))
            a_trsf2 = gp_Trsf()
            a_trsf2.SetRotation(axy, y)
            trsf = trsf*a_trsf2

        if (z!=0.0):
            axz = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0., 0., 1.))
            a_trsf3 = gp_Trsf()
            a_trsf3.SetRotation(axz, z)
            trsf = trsf*a_trsf3

        self.propagate_trsf(trsf)

    def translate(self, x=0.0, y=0.0, z=0.0):
        v = gp_Vec(x, y, z)
        a_trsf = gp_Trsf()
        a_trsf.SetTranslation(v)
        for c in self.children:
            c.propagate_trsf(a_trsf)

    def cube(self, xyz, center=False):
        cube_shape = BRepPrimAPI_MakeBox(xyz.x(), xyz.y(), xyz.z()).Shape()
        scls = SCLShape(cube_shape)
        sclp = SCLPart3(self)
        sclp.set_shape(scls)
        name = get_inc_name("cube")
        sclp.set_name(name)
        debug("Creating cube %s"%(name,))
        self.add_child_context(sclp)

    def display(self):
        debug("Display SCLPart3")
        for c in self.children:
            c.display()

        if self.shape != None:
            self.shape.display()
        display.FitAll()
        if (self.parent == None):
            start_display()

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
            a_trsf1.SetRotation(axx, x)
            self.trsf = self.trsf*a_trsf1

        if (y!=0.0):
            axy = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0., 1., 0.))
            a_trsf2 = gp_Trsf()
            a_trsf2.SetRotation(axy, y)
            self.trsf = self.trsf*a_trsf2

        if (z!=0.0):
            axz = gp_Ax1(gp_Pnt(0., 0., 0.), gp_Dir(0., 0., 1.))
            a_trsf3 = gp_Trsf()
            a_trsf3.SetRotation(axz, z)
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

    def display(self):
        debug("Display SCLProfile2")
        w = self.get_wire()
        if (w != None):
            display.DisplayShape(w)
        display.FitAll()
        start_display()

class SCLExtrude(SCLContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.body = None

    def linear_extrude(self, height=1.0):
        f = self.child.get_face()
        prism_vec = gp_Vec(0, 0, height)
        self.body = BRepPrimAPI_MakePrism(f.Face(), prism_vec)

    def display(self):
        debug("Display SCLExtrude")
        display.DisplayShape(self.body.Shape())
