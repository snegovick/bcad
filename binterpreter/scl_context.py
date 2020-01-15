from OCC.Core.AIS import AIS_ColoredShape, AIS_Line
from OCC.Core.Geom import Geom_Line, Geom_Point
from OCC.Core.Prs3d import Prs3d_LineAspect, Prs3d_Drawer
from OCC.Core.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec, gp_Pln, gp_Ax3
from OCC.Core.ChFi2d import ChFi2d_AnaFilletAlgo
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform, BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
from OCC.Extend.ShapeFactory import make_wire
from OCC.Display.SimpleGui import init_display
from OCC.Display.OCCViewer import rgb_color
from OCC.Core.TopoDS import topods, TopoDS_Compound
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_ALICEBLUE, Quantity_NOC_ANTIQUEWHITE, Quantity_NOC_BLACK
from OCC.Core.Aspect import Aspect_Grid
from OCC.Extend.TopologyUtils import TopologyExplorer

from logging import debug, info, warning, error, critical

import math

display = None
start_display = None
add_menu = None
add_functionto_menu = None

Noval = 'no val'

def is_var_set(v):
    if (v!=None) and (v!=Noval):
        return True
    return False

names = {
    "translate": 0,
    "color": 0,
    "cube": 0,
    "cylinder": 0,
    "linear_extrude": 0,
    "union": 0,
    "difference": 0,
    "profile2": 0,
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

def mk_colored_line(start, direction, color, linestyle, width):
    line = Geom_Line(start, direction)
    ais_line = AIS_Line(line)
    
    drawer = ais_line.Attributes()
    aspect = Prs3d_LineAspect(color, linestyle, width)
    drawer.SetLineAspect(aspect)
    ais_line.SetAttributes(drawer)
    return ais_line

def axis():
    center = gp_Pnt(0,0,0)
    zd = gp_Dir(0,0,10000)
    display.Context.Display(mk_colored_line(center, zd, rgb_color(0,0,1), 0, 1.0), False)

    xd = gp_Dir(1,0,0)
    display.Context.Display(mk_colored_line(center, xd, rgb_color(1,0,0), 0, 1.0), False)

    yd = gp_Dir(0,1,0)
    display.Context.Display(mk_colored_line(center, yd, rgb_color(0,1,0), 0, 1.0), False)

def scl_init_display():
    global display
    global start_display
    global add_menu
    global add_functionto_menu
    display, start_display, add_menu, add_functionto_menu = init_display()
    p = gp_Pnt(0., 0., 0.)
    d = gp_Dir(0., 0., 1.)
    a = gp_Ax3(p, d)

    #display.GetViewer().SetPrivilegedPlane(a)
    #display.GetViewer().SetRectangularGridValues(0, 0, 1, 1, 0)
    #display.GetViewer().SetRectangularGridGraphicValues(100, 100, 0)
    #display.GetViewer().Grid().SetColors(Quantity_Color(Quantity_NOC_BLACK), Quantity_Color(Quantity_NOC_BLACK))

    #display.GetViewer().ActivateGrid(0, 0)
    display.View.SetBgGradientColors(Quantity_Color(Quantity_NOC_ANTIQUEWHITE), Quantity_Color(Quantity_NOC_ANTIQUEWHITE), 2, True)

    axis()
    
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
        #display.FitAll()
        start_display()

    def get_children(self):
        children = []
        for c in self.children:
            children.append(c)
            children.extend(c.get_children())
        return children

class SCLShape(object):
    def __init__(self, shape):
        self.trsf = gp_Trsf()
        self.shape = shape

    def get_shape(self):
        return self.shape

    def transform(self, trsf):
        self.trsf = trsf
        self.transform_shape()

    def transform_shape(self):
        self.shape = BRepBuilderAPI_Transform(self.shape, self.trsf, True).Shape()

    def display(self):
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

    def color(self, r=0.0, g=0.0, b=0.0, color=None):
        pass

    def cube(self, xyz, center=False):
        cube_shape = BRepPrimAPI_MakeBox(xyz.x(), xyz.y(), xyz.z()).Shape()
        scls = SCLShape(cube_shape)
        sclp = SCLPart3(self)
        sclp.set_shape(scls)
        name = get_inc_name("cube")
        sclp.set_name(name)
        debug("Creating cube %s"%(name,))
        self.add_child_context(sclp)

    def cylinder(self, r, d, h, center=False):
        nr = None
        nh = None
        if (not is_var_set(d)) and is_var_set(r):
            nr = r
        elif is_var_set(d) and (not is_var_set(r)):
            nr = d/2.0
        elif is_var_set(d) and is_var_set(r):
            nr = d/2.0
        elif (not is_var_set(d)) and (not is_var_set(r)):
            nr = 0.5

        nh = 1.0
        if is_var_set(h):
            nh = h

        ax = gp_Ax2(gp_Pnt(0,0,0), gp_Dir(0,0,1))
        s = BRepPrimAPI_MakeCylinder(ax, nr, nh).Shape()
        scls = SCLShape(s)
        sclp = SCLPart3(self)
        sclp.set_shape(scls)
        name = get_inc_name("cylinder")
        sclp.set_name(name)
        debug("Creating cylinder %s"%(name,))
        self.add_child_context(sclp)

    def display(self):
        debug("Display SCLPart3")
        for c in self.children:
            c.display()

        if self.shape != None:
            self.shape.display()
        #display.FitAll()
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

    def display(self):
        debug("Display SCLProfile2")
        w = self.get_wire()
        if (w != None):
            display.DisplayShape(w)
        #display.FitAll()
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

    def display(self):
        debug("Display SCLUnion")
        if self.shape != None:
            self.shape.display()

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
        self.children = []

    def display(self):
        debug("Display SCLUnion")
        if self.shape != None:
            self.shape.display()

            
