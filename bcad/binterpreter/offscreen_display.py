import bcad.binterpreter.boccviewer as OCCViewer
import json

from bcad.binterpreter.rqq import *

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
        self.update_img()
        self.pipe.send(json.dumps({'rp': replies[RP_ACK]}))

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
