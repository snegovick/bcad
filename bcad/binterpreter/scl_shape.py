from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_ALICEBLUE, Quantity_NOC_ANTIQUEWHITE, Quantity_NOC_BLACK, Quantity_NOC_MATRAGRAY, Quantity_NOC_YELLOW, Quantity_NOC_PERU
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform, BRepBuilderAPI_MakeFace
from OCC.Core.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec, gp_Pln, gp_Ax3
from OCC.Display.OCCViewer import rgb_color
from OCC.Core.AIS import AIS_Shape
from OCC.Core.Prs3d import Prs3d_LineAspect, Prs3d_Drawer

from bcad.binterpreter.singleton import Singleton
from bcad.binterpreter.scl_util import unstringify, Noval, is_var_set
from bcad.binterpreter.colorname_map import colorname_map

from logging import debug, info, warning, error, critical

class SCLShape(object):
    def __init__(self, shape):
        self.trsf = gp_Trsf()
        self.shape = shape
        self.shape_color = Noval
        self.style = "main"
        self.hidden = False

    def set_hidden(self, hidden):
        self.hidden = hidden

    def is_hidden(self):
        return self.hidden

    def set_linestyle(self, name):
        if (name == "hidden"):
            debug("Set hidden line style")
            self.style = "hidden"
        if (name == "main_projection"):
            debug("Set main_projection line style")
            self.style = "main_projection"

    def set_shape_color(self, shape_color):
        self.shape_color = shape_color

    def get_shape_color(self):
        return self.shape_color

    def color(self, color):
        debug("Trying to set color: %s"%(color,))
        if (type(color)==list):
            c = color[:]
            if (len(c)<4):
                c.append(1.0)
            self.shape_color = rgb_color(c[0], c[1], c[2])
        else:
            if (unstringify(color) not in colorname_map):
                warning("Unknown color: %s"%(color,))
            else:
                self.shape_color = Quantity_Color(colorname_map[unstringify(color)])

    def get_shape(self):
        return self.shape

    def transform(self, trsf):
        self.trsf = trsf
        self.transform_shape()

    def transform_shape(self):
        self.shape = BRepBuilderAPI_Transform(self.shape, self.trsf, True).Shape()

    def display(self, writer=None):
        if self.shape != None:
            if (writer != None):
                writer.Transfer(self.shape)
            else:
                debug("Line style is %s"%(self.style,))
                ais_context = Singleton.sd.display.GetContext()                    
                if (self.style == 'hidden'):
                    ais_shp = AIS_Shape(self.shape)

                    ais_shp.SetWidth(0.1)
                    ais_shp.SetTransparency(0.10)
                    ais_shp.SetColor(rgb_color(0,0,0))
                    aspect = ais_shp.Attributes().WireAspect()
                    aspect.SetColor(rgb_color(0,0,0))
                    aspect.SetTypeOfLine(1)
                    ais_context.Display(ais_shp, True)
                elif (self.style == 'main_projection'):
                    ais_shp = AIS_Shape(self.shape)
                    ais_shp.SetWidth(5)
                    #ais_shp.SetTransparency(0)
                    #ais_shp.SetColor(rgb_color(0,0,0))
                    aspect = ais_shp.Attributes().WireAspect()
                    aspect.SetColor(rgb_color(0,0,0))
                    aspect.SetTypeOfLine(0)
                    ais_context.Display(ais_shp, True)
                else:
                    ais_context = Singleton.sd.display.GetContext()
                    ais_shp = AIS_Shape(self.shape)
                    ais_shp.SetWidth(2.0)
                    if (is_var_set(self.shape_color)):
                        ais_shp.SetColor(self.shape_color)
                    else:
                        ais_shp.SetColor(Quantity_Color(Quantity_NOC_PERU))
                    ais_context.Display(ais_shp, True)
                    
                    #Singleton.sd.display.DisplayColoredShape(self.shape, self.shape_color)
        else:
            warning("Empty shape")
