from OCC.Extend.DataExchange import write_stl_file
from OCC.Extend.TopologyUtils import TopologyExplorer, discretize_edge, is_edge, dump_topology_to_string
from OCC.Core.TopExp import TopExp_Explorer, topexp
from OCC.Core.TopAbs import (TopAbs_VERTEX, TopAbs_EDGE, TopAbs_FACE, TopAbs_WIRE,
                             TopAbs_SHELL, TopAbs_SOLID, TopAbs_COMPOUND,
                             TopAbs_COMPSOLID)
from OCC.Core.TopoDS import (topods, TopoDS_Wire, TopoDS_Vertex, TopoDS_Edge,
                             TopoDS_Face, TopoDS_Shell, TopoDS_Solid,
                             TopoDS_Compound, TopoDS_CompSolid, topods_Edge,
                             topods_Vertex, TopoDS_Iterator)
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.BRep import BRep_Tool, BRep_Tool_Curve
from OCC.Core.Geom import Geom_Curve, Geom_Line, Geom_BSplineCurve
from OCC.Core.GeomAbs import GeomAbs_Line, GeomAbs_Circle, GeomAbs_Ellipse, GeomAbs_Hyperbola, GeomAbs_Parabola, GeomAbs_BezierCurve, GeomAbs_BSplineCurve, GeomAbs_OffsetCurve, GeomAbs_OtherCurve

from logging import debug, info, warning, error, critical
import logging

import ezdxf

class SCLSTLWriter:
    def __init__(self):
        self.linear_deflection = 1.0
        self.angular_deflection = 1.0
        self.mode = "binary"
        self.shapes = []

    def set_resolution(self, linear_deflection=0.5, angular_deflection=0.3):
        self.linear_deflection = linear_deflection
        self.angular_deflection = angular_deflection

    def set_mode(self, mode):
        self.mode = mode

    def Write(self, path):
        if len(self.shapes)>0:
            u = self.shapes[0]
            for s in self.shapes[1:]:
                u = BRepAlgoAPI_Fuse(u, s).Shape()

            write_stl_file(u, path, mode=self.mode, linear_deflection=self.linear_deflection, angular_deflection=self.angular_deflection)

    def Transfer(self, shape):
        self.shapes.append(shape)

class SCLSTEPWriter:
    def __init__(self):
        self.writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", "AP203")

    def Write(self, path):
        status = step_writer.Write(path)
        if status != IFSelect_RetDone:
            raise AssertionError("Write failed")

    def Transfer(self, shape):
        self.writer.Transfer(shape, STEPControl_AsIs)

class SCLDXFWriter:
    def __init__(self):
        self.doc = ezdxf.new('R2010')
        self.msp = self.doc.modelspace()
        self.shapes = []

    def collect_dumpable_shapes(self, shape):
        if shape.ShapeType() == TopAbs_EDGE:
            points = []
            try:
                points = discretize_edge(shape, 0.25)
            except:
                points = []
            else:
                debug("Discretize done !")
            return points
            debug("edge: %s/%s"%(str(shape), self.describe_edge(shape)))
            it = TopoDS_Iterator(shape)
            points = []
            while it.More():
                shp = it.Value()
                brt = BRep_Tool()
                debug("vertex: %s"%(str(shp),))
                pnt = brt.Pnt(topods_Vertex(shp))
                points.append((pnt.X(), pnt.Y(), pnt.Z()))
                it.Next()
            return points
        else:
            lines = []
            it = TopoDS_Iterator(shape)
            while it.More():
                shp = it.Value()
                lines.append(self.collect_dumpable_shapes(shp))
                it.Next()
            return lines

    def describe_edge(self, edge):
        curve_adaptor = BRepAdaptor_Curve(edge)
        first = curve_adaptor.FirstParameter()
        last = curve_adaptor.LastParameter()
        geom_curve = curve_adaptor.Curve()
        if (geom_curve.GetType() == GeomAbs_Line):
            return "Is line"
        elif (geom_curve.GetType() == GeomAbs_Circle):
            return "Is circle"
        elif (geom_curve.GetType() == GeomAbs_Ellipse):
            return "Is ellipse"
        elif (geom_curve.GetType() == GeomAbs_Hyperbola):
            return "Is hyperbola"
        elif (geom_curve.GetType() == GeomAbs_Parabola):
            return "Is parabola"
        elif (geom_curve.GetType() == GeomAbs_BezierCurve):
            return "Is bezier"
        elif (geom_curve.GetType() == GeomAbs_BSplineCurve):
            return "Is bspline"
        elif (geom_curve.GetType() == GeomAbs_OffsetCurve):
            return "Is offset"
        elif (geom_curve.GetType() == GeomAbs_OtherCurve):
            return "Is other"

    def Write(self, path):
        from bcad.binterpreter.scl_context import SCLProjection
        p = SCLProjection(None)
        p.hlr_project(self.shapes)
        shapes = []
        for c in p.children:
            if c.shape != None:
                dump_topology_to_string(c.shape.get_shape())
                shapes.append(c.shape.get_shape())
        lines = []
        for s in shapes:
            lines.extend(self.collect_dumpable_shapes(s))
        #debug("Lines: %s"%(str(lines),))
        ctr = 0

        for l in lines:
            #debug ("l: %s"%(str(l),))
            if len(l)>1:
                s = l[0][:2]
                for p in l[1:]:
                    e = p[:2]
                    self.msp.add_line(s, e)
                    s = e
            # e = l[1][:2]
            # 
        self.doc.saveas(path)
        return
        
        for s in shapes:
            exp = TopExp_Explorer()
            exp.Init(s, TopAbs_EDGE)
            while exp.More():
                edge = exp.Value()
                if not is_edge(edge):
                    warning("Is not an edge.")
                if exp.Value().IsNull():
                    warning("TopoDS_Edge is null")

                curve_adaptor = BRepAdaptor_Curve(edge)
                first = curve_adaptor.FirstParameter()
                last = curve_adaptor.LastParameter()
                geom_curve = curve_adaptor.Curve()
                #edges.append(exp.Current())
                # first = topexp.FirstVertex(exp.Value())
                # last  = topexp.LastVertex(exp.Value())
                
                # # Take geometrical information from vertices.
                # pnt_first = BRep_Tool.Pnt(first)
                # pnt_last = BRep_Tool.Pnt(last)

                # a, b = BRep_Tool.Curve(exp.Value())
                exp.Next()
                if (geom_curve.GetType() == GeomAbs_Line):
                    debug("Is line")
                elif (geom_curve.GetType() == GeomAbs_Circle):
                    debug("Is circle")
                elif (geom_curve.GetType() == GeomAbs_Ellipse):
                    debug("Is ellipse")
                elif (geom_curve.GetType() == GeomAbs_Hyperbola):
                    debug("Is hyperbola")
                elif (geom_curve.GetType() == GeomAbs_Parabola):
                    debug("Is parabola")
                elif (geom_curve.GetType() == GeomAbs_BezierCurve):
                    debug("Is bezier")
                elif (geom_curve.GetType() == GeomAbs_BSplineCurve):
                    debug("Is bspline")
                elif (geom_curve.GetType() == GeomAbs_OffsetCurve):
                    debug("Is offset")
                elif (geom_curve.GetType() == GeomAbs_OtherCurve):
                    #debug("Is other")
                    continue
                    #self.msp.add_line()

                pts = discretize_edge(edge)
                debug("Curve[%i]: %s / %s"%(ctr, str(geom_curve.GetType()),str(edge)))
                ctr+=1
            #for e in TopologyExplorer(s).edges():

        #self.writer.saveas(path)

    def Transfer(self, shape):
        self.shapes.append(shape)

