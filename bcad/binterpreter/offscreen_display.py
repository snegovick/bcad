import bcad.binterpreter.boccviewer as OCCViewer

from bcad.binterpreter.singleton import Singleton
from bcad.binterpreter.rqq import *

import json

class offscreenViewer3d:
    def __init__(self, *kargs):
        self.pt = (0,0)
        self.pipe = None
        self.img = None

    def init_driver(self):
        self._display = OCCViewer.OffscreenRenderer()
        #self._display.SetWindow(self.GetHandle(), )
        self._display.Create()
        # background gradient
        self._display.SetModeShaded()
        self._inited = True

    def set_pipe(self, pipe):
        self.pipe = pipe

    def set_img(self, img):
        self.img = img

    def repaint(self):
        self._display.Repaint()

    def make_current(self):
        self._display.MakeCurrent()

    def swap_buffers(self):
        self._display.SwapBuffers()

    def update_img(self):
        data = self._display.GetImageData(1)
        self.img.buf[:len(data)] = data        

    def call_start_rotation(self, x, y):
        print("call start rotation", x, y)
        self._display.StartRotation(int(x), int(y))
        self.update_img()
        self.pipe.send(json.dumps({'rp': replies[RP_ACK]}))

    def call_rotate(self, x, y):
        #print("call rotate", x, y)
        self._display.Rotation(int(x), int(y))
        self.update_img()
        self.pipe.send(json.dumps({'rp': replies[RP_ACK]}))

    def call_set_size(self, w, h):
        print("call set size", w, h)
        self._display.SetSize(w, h)
        self.repaint()
        self.update_img()
        self.pipe.send(json.dumps({'rp': replies[RP_ACK_SET_SIZE], 'args': [w, h]}))

    def call_load_image(self):
        print("call load image")
        self.repaint()
        self.update_img()
        print("call load image DONE")
        self.pipe.send(json.dumps({'rp': replies[RP_ACK]}))

    def call_scroll(self, delta):
        print("call scroll", delta)
        zoom_factor = 1.0
        if delta > 0:
            zoom_factor = 2.
        else:
            zoom_factor = 0.5
        self._display.ZoomFactor(zoom_factor)
        self.update_img()
        self.pipe.send(json.dumps({'rp': replies[RP_ACK]}))

    def call_move(self, x, y):
        self._display.MoveTo(int(x), int(y))
        self.update_img()
        self.pipe.send(json.dumps({'rp': replies[RP_ACK]}))

    def call_pan(self, x, y):
        print("call pan", x, y)
        self._display.Pan(int(x), -int(y))
        self.update_img()
        self.pipe.send(json.dumps({'rp': replies[RP_ACK]}))

    def call_check_redraw(self):
        if Singleton.should_redraw == True:
            Singleton.should_redraw = False
            print("should redraw")
            self.update_img()
            self.pipe.send(json.dumps({'rp': replies[RP_ACK]}))
        else:
            self.pipe.send(json.dumps({'rp': replies[RP_NOP]}))

    def call_get_object_tree(self):
        self.pipe.send(json.dumps({'rp': replies[RP_ACK_GET_OBJECT_TREE], 'args': Singleton.scl.objects}))

    def call_set_view(self, name):
        print("Set view:", name)
        if name == 'left':
            self._display.View_Left()
        elif name == 'right':
            self._display.View_Right()
        elif name == 'top':
            self._display.View_Top()
        elif name == 'bottom':
            self._display.View_Bottom()
        elif name == 'front':
            self._display.View_Front()
        elif name == 'rear':
            self._display.View_Rear()
        elif name == 'iso1':
            self._display.View_Iso1()
        elif name == 'iso2':
            self._display.View_Iso2()
        elif name == 'iso3':
            self._display.View_Iso3()
        elif name == 'iso4':
            self._display.View_Iso4()
        elif name == 'iso5':
            self._display.View_Iso5()
        elif name == 'iso6':
            self._display.View_Iso6()
        elif name == 'iso7':
            self._display.View_Iso7()
        elif name == 'iso8':
            self._display.View_Iso8()
        self.update_img()
        self.pipe.send(json.dumps({'rp': replies[RP_ACK]}))
