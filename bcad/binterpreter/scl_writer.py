from OCC.Extend.DataExchange import write_stl_file
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut

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
