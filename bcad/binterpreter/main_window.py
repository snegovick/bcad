from bcad.binterpreter.rqq import *
from bcad.binterpreter.offscreen_display import offscreenViewer3d
from bcad.binterpreter.glfw_display import glfwViewer3d

import imgui
from imgui.integrations.glfw import GlfwRenderer

import json

class MainWindow():
    def __init__(self, gui=True, pipe=None, img=None):
        self.use_imgui = gui
        self.use_occt = not gui
        self.please_stop = False
        self.rqq = rqQueue()
        self.texture_updated = False
        self.prev_pos = [0, 0]
        self.offscreen_view_size = [0,0]

        if self.use_imgui:
            print("Creating IMGUI context")
            imgui.create_context()
        else:
            print("IMGUI disabled")
        # Create a windowed mode window and its OpenGL context

        if self.use_imgui:
            self.canva = glfwViewer3d()
            self.canva.set_pipe(pipe)
            self.canva.set_img(img)
            self.canva.init_driver()
            self.impl = GlfwRenderer(self.canva.window)
        else:
            self.canva = offscreenViewer3d()
            self.canva.set_pipe(pipe)
            self.canva.set_img(img)

    def parse_reply(self):
        rp = self.canva.pipe.recv()
        jdata = json.loads(rp)
        if jdata['rp'] == replies[RP_IMAGE_DATA]:
            if (self.offscreen_view_size[0] == self.canva.view_size[0]) and (self.offscreen_view_size[1] == self.canva.view_size[1]):
                self.canva.set_image(self.canva.view_size[0], self.canva.view_size[1], data=self.canva.img.buf)
            else:
                self.canva.set_image_black()
            self.canva.reply_received()
        elif jdata['rp'] == replies[RP_ACK]:
            if (self.offscreen_view_size[0] == self.canva.view_size[0]) and (self.offscreen_view_size[1] == self.canva.view_size[1]):
                self.canva.set_image(self.canva.view_size[0], self.canva.view_size[1], data=self.canva.img.buf)
            else:
                self.canva.set_image_black()
            self.canva.reply_received()
        elif jdata['rp'] == replies[RP_ACK_SET_SIZE]:
            self.offscreen_view_size = [jdata['args'][0], jdata['args'][1]]
            if (self.offscreen_view_size[0] == self.canva.view_size[0]) and (self.offscreen_view_size[1] == self.canva.view_size[1]):
                self.canva.set_image(self.canva.view_size[0], self.canva.view_size[1], data=self.canva.img.buf)
            else:
                self.canva.set_image_black()
            self.canva.reply_received()

    def mainloop(self):
        if self.use_imgui:
            self.canva.init_shader()
            self.canva.create_objects()
            self.rqq.rq_set_size(self.canva.view_size[0], self.canva.view_size[1])
            print("Waiting set size reply")
            self.rqq.process(self.canva)
            self.parse_reply()
            self.rqq.rq_load_image()
            while (not self.canva.should_close() and (not self.please_stop)):
                self.canva.proc()
                if self.canva.get_need_resize():
                    self.canva.set_image_black()
                    self.rqq.rq_set_size(self.canva.view_size[0], self.canva.view_size[1])
                    self.canva.start_frame()
                    self.canva.swap_buffers()
                    self.canva.poll_events()
                    continue
                self.rqq.process(self.canva)
                if self.canva.pipe.poll() == True:
                    self.parse_reply()
                self.impl.process_inputs()
                imgui.new_frame()

                if imgui.begin_main_menu_bar():
                    if imgui.begin_menu("File", True):
                        clicked_quit, selected_quit = imgui.menu_item("Quit", 'Ctrl+Q', False, True)
                        if clicked_quit:
                            self.please_stop = True
                        imgui.end_menu()
                    if imgui.begin_menu("Render", True):
                        imgui.menu_item("Save", None, False, True)
                        imgui.end_menu()
                    imgui.end_main_menu_bar()

                # right button rotation
                if imgui.is_mouse_down(1):
                    if self.canva.drag_start == None:
                        pos = imgui.get_io().mouse_pos
                        self.canva.drag_start = [pos[0], pos[1]]
                        self.rqq.rq_start_rotation(self.canva.drag_start[0], self.canva.drag_start[1])
                    else:
                        pos = imgui.get_io().mouse_pos
                        self.pt = [pos[0], pos[1]]
                        self.rqq.rq_rotate(self.pt[0], self.pt[1])
                # left button panning
                elif imgui.is_mouse_down(0):
                    if self.canva.drag_start == None:
                        pos = imgui.get_io().mouse_pos
                        self.canva.drag_start = [pos[0], pos[1]]
                        self.prev_pos = pos
                    else:
                        pos = imgui.get_io().mouse_pos
                        if not self.prev_pos == pos:
                            self.rqq.rq_pan(pos[0]-self.prev_pos[0], pos[1]-self.prev_pos[1])
                            self.prev_pos = pos
                # wheel button scrolling
                else:
                    self.canva.drag_start = None
                    mw = imgui.get_io().mouse_wheel
                    pos = imgui.get_io().mouse_pos
                    if mw != 0:
                        self.rqq.rq_scroll(mw)
                    else:
                        if not self.prev_pos == pos:
                            self.rqq.rq_move(pos[0], pos[1])
                            self.prev_pos = pos

                self.canva.start_frame()
                imgui.render()
                draw_data = imgui.get_draw_data()
                self.impl.render(draw_data)
                self.canva.swap_buffers()
                self.canva.poll_events()
            self.canva.rq_stop()
            self.canva.pipe.close()
            print("GUI stopped")
        else:
            while True:
                rq = self.canva.pipe.recv()
                jdata = json.loads(rq)
                #print("rq:", rq, "jdata:", type(jdata))
                if jdata['rq'] == requests[RQ_LOAD_IMAGE]:
                    tex = self.canva.call_load_image()
                elif jdata['rq'] == requests[RQ_START_ROTATION]:
                    self.canva.call_start_rotation(jdata['args'][0], jdata['args'][1])
                elif jdata['rq'] == requests[RQ_ROTATE]:
                    self.canva.call_rotate(jdata['args'][0], jdata['args'][1])
                elif jdata['rq'] == requests[RQ_SET_SIZE]:
                    self.canva.call_set_size(jdata['args'][0], jdata['args'][1])
                elif jdata['rq'] == requests[RQ_SCROLL]:
                    self.canva.call_scroll(jdata['args'])
                elif jdata['rq'] == requests[RQ_MOVE]:
                    self.canva.call_move(jdata['args'][0], jdata['args'][1])
                elif jdata['rq'] == requests[RQ_PAN]:
                    self.canva.call_pan(jdata['args'][0], jdata['args'][1])
                elif jdata['rq'] == requests[RQ_STOP]:
                    break
            self.canva.img.unlink()
            self.canva.pipe.close()
            print("OCCT stopped")
