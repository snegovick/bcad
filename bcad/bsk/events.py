from __future__ import absolute_import, division, print_function

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import time
import sys
import imp
import os

from logging import debug, info, warning, error, critical
from bsuite.bsk.util import dbgfname

from bsuite.bsk.singleton import Singleton
from bsuite.bsk.state import State
from bsuite.bsk.project import project
from bsuite.bsk.elements import EMode, ELine
from bsuite.bsk.calc_utils import sign

def screen_to_pointer(x, y):
    offset = Singleton.state.get_offset()
    screen_offset = Singleton.state.get_screen_offset()
    scale = Singleton.state.get_scale()
    px = (x-offset[0])/scale[0]
    py = -(y-offset[1])/scale[1]
    return px, py

def cursor_with_snap(px, py):
    c = (0,0)
    step = Singleton.state.step
    scale = Singleton.state.get_scale()
    offset = Singleton.state.get_offset()
    xof = int((px+sign(px)*step/2.0)/(step))*step
    yof = int((py+sign(py)*step/2.0)/(step))*step
    dist2 = (xof-px)**2+(yof-py)**2
    elements = Singleton.state.elements
    snap_points = [(xof, yof)]
    dists = [dist2]
    for e in elements:
        points = e.get_snap_points()
        snap_points+=points
    for p in snap_points[1:]:
        ptx = p[0]
        pty = p[1]
        dsq = (ptx-px)**2+(pty-py)**2
        dists.append(dsq)
    #debug("snap points: %s"%(snap_points,))
    #debug("dists: %s"%(dists,))
    min_dist = min(dists)
    idx = dists.index(min_dist)
    sp = snap_points[idx]
    if (min_dist<step/scale[0]*2.0):
        c = (sp[0]*scale[0]+offset[0], -sp[1]*scale[1]+offset[1])
        debug("snap: %.2f,%.2f"%(c[0], c[1]))
    else:
        c = (px*scale[0]+offset[0], -py*scale[1]+offset[1])
    return c

class EVEnum(object):
    main_start = "main_start"
    sketcher_start = "sketcher_start"
    pointer_motion = "pointer_motion"
    scroll_up = "scroll_up"
    scroll_down = "scroll_down"
    hscroll = "hscroll"
    vscroll = "vscroll"
    screen_left_press = "screen_left_press"
    screen_left_release = "screen_left_release"
    line_2point_click = "line_2point_click"
    escape = "escape"
    
class EventProcessor(object):
    ee = EVEnum()
    event_list = []
    selected_elements = []
    selected_path = None
    selected_tool_operation = None
    left_press_start = None
    pointer_position = None
    cursor_position = None
    shift_pressed = False
    ctrl_pressed = False
    last_point = None

    current_element = None
    current_mode = None

    def __init__(self):
        Singleton.ee = self.ee
        Singleton.ep = self
        self.started = False
        self.events = {
            self.ee.main_start: [self.main_start],
            self.ee.sketcher_start: [self.sketcher_start],
            self.ee.pointer_motion: [self.pointer_motion],
            self.ee.scroll_up: [self.scroll_up],
            self.ee.scroll_down: [self.scroll_down],
            self.ee.hscroll: [self.hscroll],
            self.ee.vscroll: [self.vscroll],
            self.ee.screen_left_press: [self.screen_left_press],
            self.ee.screen_left_release: [self.screen_left_release],
            self.ee.line_2point_click: [self.line_2point_click],
            self.ee.escape: [self.escape],
        }

    def reset(self):
        self.selected_elements = []
        self.left_press_start = None

    def append_event_processor(self, event, proc):
        self.events[event].append(proc)

    def prepend_event_processor(self, event, proc):
        self.events[event].insert(0, proc)

    def set_event(self, event, proc_list):
        self.events[event] = proc_list

    def push_event(self, event, *args):
        self.event_list.append((event, args))

    def process(self):
        if self.started == False:
            self.push_event(self.ee.main_start, None)
            self.started = True
        event_list = self.event_list[:]
        self.event_list = []
        for e, args in event_list:
            if e in self.events:
                for p in self.events[e]:
                    r = p(args)
                    if (r == False):
                        break
            else:
                warning("  Unknown event:"+str(e)+" args: "+str(args))
                warning("  Please report")

    def screen_to_cursor_with_snap(self, sx, sy):
        px, py = screen_to_pointer(sx, sy)
        self.pointer_position = (px, py)
        self.pointer_position_actual = (sx, sy)
        cx, cy = cursor_with_snap(px, py)
        self.cursor_position = (cx,cy)
        self.pointer_position = screen_to_pointer(cx, cy)
        return cx, cy

    def main_start(self, args):
        dbgfname()
        offset = Singleton.state.get_offset()
        cx = (offset[0])
        cy = -(offset[1])
        self.cursor_position = (cx,cy)

    def sketcher_start(self, args):
        dbgfname()
        debug("  sketcher start")
        self.reset()
        Singleton.state = State()
        self.pointer_position = (0,0)
        project.push_state(Singleton.state, "sketcher_start")
        self.mw.widget.update()

    def pointer_motion(self, args):
        #dbgfname()
        cx, cy = self.screen_to_cursor_with_snap(args[0][0], args[0][1])
        px, py = self.pointer_position
        
        if (self.current_mode == EMode.eline_2point):
            if (self.current_element != None):
                self.current_element.end=(px, py)

        #self.mw.cursor_pos_label.set_text("cur: %.3f:%.3f"%(cx, cy))
        self.mw.widget.update()

    def scale_generic(self, direction="up"):
        small_step = 0.1
        big_step = 1.5
        if (direction != "up"):
            small_step = -0.1
            big_step = 1.0/1.5

        osx, osy = Singleton.state.scale
        if Singleton.state.scale[0]<=0.01:
            Singleton.state.scale = (Singleton.state.scale[0]+small_step, Singleton.state.scale[1]+small_step)
        else:
            Singleton.state.scale = (Singleton.state.scale[0]*big_step, Singleton.state.scale[1]*big_step)
        tx, ty = Singleton.state.get_offset()
        sx, sy = Singleton.state.get_screen_size()
        px, py = self.pointer_position
        pcx, pcy = self.pointer_position_actual
        nsx, nsy = Singleton.state.scale
        scx, scy = Singleton.state.get_screen_offset()
        ncx = (pcx-scx-px*nsx)
        ncy = (pcy-scy+py*nsy)
        Singleton.state.set_base_offset((ncx, ncy))

    def scroll_up(self, args):
        dbgfname()
        debug("  scroll up")
        if self.shift_pressed:
            offset = Singleton.state.get_base_offset()
            Singleton.mw.widget_vscroll.set_value(-(offset[1]+10*Singleton.state.scale[0]))
        elif self.ctrl_pressed:
            offset = Singleton.state.get_base_offset()
            Singleton.mw.widget_hscroll.set_value(-(offset[0]+10*Singleton.state.scale[0]))
        else:
            self.scale_generic("up")
        self.mw.widget.update()

    def scroll_down(self, args):
        dbgfname()
        debug("  scroll down")
        if self.shift_pressed:
            offset = Singleton.state.get_base_offset()
            Singleton.mw.widget_vscroll.set_value(-(offset[1]-10*Singleton.state.scale[0]))
        elif self.ctrl_pressed:
            offset = Singleton.state.get_base_offset()
            Singleton.mw.widget_hscroll.set_value(-(offset[0]-10*Singleton.state.scale[0]))
        else:
            self.scale_generic("down")
        self.mw.widget.update()

    def hscroll(self, args):
        dbgfname()
        debug("  hscroll: "+str(args))
        debug("  "+str(args[0][0].get_value()))
        offset = Singleton.state.get_base_offset()
        Singleton.state.set_base_offset((-args[0][0].get_value(), offset[1]))
        self.mw.widget.update()

    def vscroll(self, args):
        dbgfname()
        debug("  vscroll: "+str(args))
        debug("  "+str(args[0][0].get_value()))
        offset = Singleton.state.get_base_offset()
        Singleton.state.set_base_offset((offset[0], -args[0][0].get_value()))
        self.mw.widget.update()

    def screen_left_release(self, args):
        dbgfname()
        cx, cy = self.screen_to_cursor_with_snap(args[0][0], args[0][1])

    def screen_left_press(self, args):
        dbgfname()
        cx, cy = self.screen_to_cursor_with_snap(args[0][0], args[0][1])
        px, py = self.pointer_position
        if (self.current_mode == EMode.eline_2point):
            if (self.current_element == None):
                self.current_element = ELine(start=(px, py), end=(px, py))
            else:
                self.current_element.end=(px, py)
                Singleton.state.elements.append(self.current_element)
                self.current_element = ELine(start=(px, py), end=(px, py))
            self.mw.widget.update()

    def line_2point_click(self, args):
        dbgfname()
        self.current_mode = EMode.eline_2point

    def escape(self, arg):
        dbgfname()
        if self.current_element != None:
            self.current_element = None
        self.current_mode = None
        self.mw.widget.update()

ee = EVEnum()
ep = EventProcessor()
