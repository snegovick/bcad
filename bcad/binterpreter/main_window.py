from bcad.binterpreter.rqq import *
from bcad.binterpreter.offscreen_display import offscreenViewer3d
from bcad.binterpreter.glfw_display import glfwViewer3d

from bcad.binterpreter.events import EVEnum, EventProcessor, ee, ep
from bcad.binterpreter.singleton import Singleton

import imgui
from imgui.integrations.glfw import GlfwRenderer

import json
import time

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
            self.objtree = None
            self.show_objtree = True
            self.show_views = True
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
        elif jdata['rp'] == replies[RP_ACK_GET_OBJECT_TREE]:
            objtree = jdata['args']
            self.objtree = objtree
            self.canva.reply_received()
        elif jdata['rp'] == replies[RP_NOP]:
            self.canva.reply_received()

    def object_node(self, node):
        if node:
            if node['children']:
                if (imgui.tree_node(node['name'])):
                    for c in node['children']:
                        self.object_node(c)
                    imgui.tree_pop()
            else:
                imgui.text(node['name'])

    def object_tree(self, first_frame, x, y, w, h):
        if first_frame:
            imgui.core.set_next_window_position(x, y, imgui.ALWAYS)
        imgui.begin("Objects")

        if self.objtree:
            self.object_node(self.objtree)

        hovered = imgui.core.is_window_hovered()
        wh = imgui.core.get_window_size()

        imgui.end()
        return hovered, wh

    def views_list(self, first_frame, x, y, w, h):
        if first_frame:
            imgui.core.set_next_window_position(x, y, imgui.ALWAYS)
        imgui.begin("Views")
        if imgui.button('Left'):
            self.rqq.rq_set_view('left')
        elif imgui.button('Right'):
            self.rqq.rq_set_view('right')
        elif imgui.button('Top'):
            self.rqq.rq_set_view('top')
        elif imgui.button('Bottom'):
            self.rqq.rq_set_view('bottom')
        elif imgui.button('Front'):
            self.rqq.rq_set_view('front')
        elif imgui.button('Rear'):
            self.rqq.rq_set_view('rear')
        elif imgui.button('Iso1'):
            self.rqq.rq_set_view('iso1')
        elif imgui.button('Iso2'):
            self.rqq.rq_set_view('iso2')
        elif imgui.button('Iso3'):
            self.rqq.rq_set_view('iso3')
        elif imgui.button('Iso4'):
            self.rqq.rq_set_view('iso4')
        elif imgui.button('Iso5'):
            self.rqq.rq_set_view('iso5')
        elif imgui.button('Iso6'):
            self.rqq.rq_set_view('iso6')
        elif imgui.button('Iso7'):
            self.rqq.rq_set_view('iso7')
        elif imgui.button('Iso8'):
            self.rqq.rq_set_view('iso8')
        hovered = imgui.core.is_window_hovered()
        wh = imgui.core.get_window_size()

        imgui.end()
        return hovered, wh

    def mainloop(self):
        if self.use_imgui:
            self.canva.init_shader()
            self.canva.create_objects()
            
            self.rqq.rq_set_size(self.canva.view_size[0], self.canva.view_size[1])
            print("Waiting set size reply")
            self.rqq.process(self.canva)
            self.parse_reply()
            
            self.rqq.rq_get_object_tree()
            print("Waiting get object tree reply")
            self.rqq.process(self.canva)
            self.parse_reply()
            
            self.rqq.rq_load_image()
            last = time.time()
            first_frame = True
            while (not self.canva.should_close() and (not self.please_stop)):
                current = time.time()
                menu_bar_w_h = (0,0)
                objtree_w_h = (0,0)
                views_w_h = (0,0)
                self.canva.proc()
                if self.canva.get_need_resize():
                    self.canva.set_image_black()
                    self.rqq.rq_set_size(self.canva.view_size[0], self.canva.view_size[1])
                    self.canva.start_frame()
                    self.canva.swap_buffers()
                    self.canva.poll_events()
                    continue
                qlen = self.rqq.process(self.canva)
                if (current-last)>1:
                    last = current
                    self.rqq.rq_check_redraw()
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
                    if imgui.begin_menu("View", True):
                        clicked_view_objtree, selected_view_objtree = imgui.menu_item("Show object tree", None, False, True)
                        if clicked_view_objtree:
                            self.show_objtree = not(self.show_objtree)
                        clicked_view_views, selected_view_views = imgui.menu_item("Show views", None, False, True)
                        if clicked_view_views:
                            self.show_views = not(self.show_views)
                        imgui.end_menu()
                    wh = imgui.core.get_window_size()
                    menu_bar_w_h = wh
                    imgui.end_main_menu_bar()

                hovered = False
                if self.show_objtree:
                    hovered, objtree_w_h = self.object_tree(first_frame, 0, menu_bar_w_h[1], 0, 0)

                if self.show_views:
                    hovered, views_w_h = self.views_list(first_frame, objtree_w_h[0], menu_bar_w_h[1], 0, 0)

                if not hovered:
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
                    elif imgui.is_mouse_down(2):
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

                first_frame = False
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
                ep.process()
                if self.canva.pipe.poll() == True:
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
                    elif jdata['rq'] == requests[RQ_CHECK_REDRAW]:
                        self.canva.call_check_redraw()
                    elif jdata['rq'] == requests[RQ_GET_OBJECT_TREE]:
                        self.canva.call_get_object_tree()
                    elif jdata['rq'] == requests[RQ_SET_VIEW]:
                        self.canva.call_set_view(jdata['args'])
                    elif jdata['rq'] == requests[RQ_STOP]:
                        break
                time.sleep(0.01)
            self.canva.img.unlink()
            self.canva.pipe.close()
            print("OCCT stopped")
