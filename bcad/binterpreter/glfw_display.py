#!/usr/bin/env python3
from __future__ import print_function

#import cProfile

import logging
import os
import sys
import json
import signal
import numpy as np

import bcad.binterpreter.boccviewer as OCCViewer
from bcad.binterpreter.rqq import *

import glfw
import OpenGL.GL as gl
import OpenGL.GL.shaders as shaders

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)
    
class glfwViewer3d:
    def __init__(self):
        self.pt = [0,0]
        self.drag_start = None
        self.pipe = None
        self.view_size = [1280, 1024]
        self.waiting_reply = False
        self.need_resize = False

    def set_pipe(self, pipe):
        self.pipe = pipe

    def set_img(self, img):
        self.img = img

    def reply_received(self):
        self.waiting_reply = False

    def is_waiting_reply(self):
        return self.waiting_reply

    def rq_stop(self):
        print("rq render stop")
        self.waiting_reply = True
        self.pipe.send(json.dumps({'rq': requests[RQ_STOP]}))

    def send_rq(self, rq):
        self.waiting_reply = True
        self.pipe.send(rq)

    # def mouse_button_event(self, win, button, action, mods):
    #     if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_RIGHT:
    #         self.drag_start = self.pt[:]
    #         self.rq_start_rotation(self.drag_start[0], self.drag_start[1])

    # def mouse_move_event(self, win, x, y):
    #     self.pt = (int(x), int(y))
    #     if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_RIGHT):
    #         self.cursor = "rotate"
    #         self.rq_rotate(self.pt[0], self.pt[1])
    #         self._drawbox = False

    def init_driver(self):
        if not glfw.init():
            return
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
        
        self.window = glfw.create_window(1280, 1024, "BCAD", None, None)
        if not self.window:
            glfw.terminate()
            return
        
        # Make the window's context current
        glfw.make_context_current(self.window)
        
        print("OpenGL version: ", gl.glGetString(gl.GL_VERSION))
        print("GLSL version: ", gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION))
        print("Vendor: ", gl.glGetString(gl.GL_VENDOR))
        print("Renderer: ", gl.glGetString(gl.GL_RENDERER))
        # glfw.set_window_size_callback(self.window, self.resize_event)
        # glfw.set_scroll_callback(self.window, self.scroll_event)
        # glfw.set_mouse_button_callback(self.window, self.mouse_button_event)
        # glfw.set_cursor_pos_callback(self.window, self.mouse_move_event)
        # glfw.set_key_callback(self.window, self.keyPressEvent)

    def proc(self):
        w, h = glfw.get_window_size(self.window)
        if (self.view_size[0] != w) or (self.view_size[1] != h):
            self.view_size = (w, h)
            self.need_resize = True

    def get_need_resize(self):
        need_resize = self.need_resize
        self.need_resize = False
        return need_resize

    def draw_image_quad(self):
        gl.glUseProgram(self.shader);

        gl.glBindVertexArray(self.vao); 
        gl.glEnableVertexAttribArray(0);
        gl.glEnableVertexAttribArray(1);
        #draw
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6);
        #unbind
        gl.glBindVertexArray(0); 
        gl.glDisableVertexAttribArray(0);
        gl.glDisableVertexAttribArray(1);

    def init_shader(self):
        #positions        colors               texture coords
        quad = [-1.0,  1.0, 0.0, 1.0,
                -1.0, -1.0, 0.0, 1.0,
                1.0, -1.0, 0.0, 1.0,
                1.0, -1.0, 0.0, 1.0,
                1.0,  1.0, 0.0, 1.0,
                -1.0,  1.0, 0.0, 1.0]
        self.quad = np.array(quad, dtype=np.float32)

        texcoords = [0.0, 1.0,
                    0.0, 0.0,
                    1.0, 0.0,
                    1.0, 0.0,
                    1.0, 1.0,
                    0.0, 1.0]

        # convert to 32bit float
        self.texcoords = np.array(texcoords, dtype = np.float32)
        VERTEX_SHADER = """
        #version 330 core
        layout(location = 0) in vec4 pos;
        layout(location = 1) in vec2 tex;
        smooth out vec2 UV;
        //uniform mat4 MVP;
        void main() {
          gl_Position = pos;
          UV = tex;
        }
        """

        FRAGMENT_SHADER = """
        #version 330 core
        smooth in vec2 UV;
        out vec3 outColor;
        uniform sampler2D cltexture;
        void main() {
          outColor = texture(cltexture, UV).rgb;
        }
        """

        # Compile The Program and shaders

        shader = shaders.compileProgram(shaders.compileShader(VERTEX_SHADER, gl.GL_VERTEX_SHADER),
                                        shaders.compileShader(FRAGMENT_SHADER, gl.GL_FRAGMENT_SHADER))
        self.shader = shader

    def create_objects(self):
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        #geometry buffer
        self.quadvbo = gl.glGenBuffers(1);
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.quadvbo);
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 6 * 4 * 4, self.quad, gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(0, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        #texture coordinate buffer
        self.texbo = gl.glGenBuffers(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.texbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 12 * 4, self.texcoords, gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None);
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0); 

        gl.glBindVertexArray(0)

        # create texture 
        self.texture = gl.glGenTextures(1)

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, self.view_size[0], self.view_size[1], 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, b'\0'*self.view_size[0]*self.view_size[1]*4)

        #optional
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0);

        gl.glUseProgram(self.shader);

        #extract ids of shader variables
        #GLint mvpID = glGetUniformLocation(glprogram, "MVP");
        #assert(mvpID>=0);

        self.texid = gl.glGetUniformLocation(self.shader, "cltexture");
        #only need texture unit 0
        gl.glActiveTexture(gl.GL_TEXTURE0);
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture);
        gl.glUniform1i(self.texid, 0);

    def set_image(self, w, h, data=None):
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data)

    def set_image_black(self):
        self.set_image(self.view_size[0], self.view_size[1], b'\0'*self.view_size[0]*self.view_size[1]*4)

    def start_frame(self):
        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        
        w, h = glfw.get_framebuffer_size(self.window);
        gl.glViewport(0, 0, w, h)

        self.draw_image_quad()

    def should_close(self):
        return glfw.window_should_close (self.window)

    def poll_events(self):
        glfw.poll_events()

    def swap_buffers(self):
        glfw.swap_buffers(self.window)

def RunGLFWDisplay(target_proc=None, cmdline_args=None):

    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeBox
    #from OCC.Core.Graphic3d import Graphic3d_BufferType
    from multiprocessing import Process, Pipe, Value, shared_memory
    import time
    import ctypes

    from bcad.binterpreter.main_window import MainWindow
    from bcad.binterpreter.offscreen_display import offscreenViewer3d
    from bcad.binterpreter.args import parse_args

    def occt_proc(pipe, img, cmdline):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        win = MainWindow(False, pipe, img)
        print("Init driver")
        win.canva.init_driver()
        print("Enable triedron")
        win.canva._display.display_triedron()
        win.canva._display.DisplayShape(BRepPrimAPI_MakeBox(1, 1, 1).Shape(), update=True)
        background_gradient_color1=[206, 215, 222]
        background_gradient_color2=[128, 128, 128]
        win.canva._display.set_bg_gradient_color(background_gradient_color1, background_gradient_color2)
        #print("Display test")
        #win.canva._display.Test()
        print("Repaint")
        win.canva.repaint()
        win.mainloop()

    class App:
        def __init__(self):
            self.win = None

        def run(self, target_proc, cmdline_args=None):
            self.img = shared_memory.SharedMemory(create=True, size=4096*2160*4) # true 4k for now, just in case. TODO: realloc dynamically
            parent_conn, child_conn = Pipe()
            self.parent_conn = parent_conn
            self.child_conn = child_conn
            if target_proc == None:
                target_proc = occt_proc
            self.p = Process(target=target_proc, args=(child_conn, self.img, cmdline_args))
            self.p.start()
            self.win = MainWindow(True, parent_conn, self.img)
                
            signal.signal(signal.SIGINT, self.sigint)
            self.win.mainloop()
            self.p.join()

        def sigint(self, sig, frame):
            print("Stopping BCAD")
            self.win.please_stop = True
            self.win.canva.rq_stop()
            self.p.join()
            exit(0)

    args = parse_args(cmdline_args)
    if args.output != None and target_proc != None:
        target_proc(None, None, cmdline_args)
    else:
        app = App()
        app.run(target_proc)

if __name__ == "__main__":
    RunGLFWDisplay()
#    cProfile.run('TestGLFWDisplay()')
