import cairo
import math
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from gi.repository import Pango
from gi.repository import PangoCairo

from bsuite.bsk.singleton import Singleton
from bsuite.bsk.events import ep, ee

from logging import debug, info, warning, error, critical
#try:
#    gi.require_foreign("cairo")
#except ImportError:
#    print("No pycairo integration :(")

class CairoScreen(Gtk.DrawingArea):
    __gtype_name__ = 'CairoScreen'
    type_name = 'CairoScreen'
    # Draw in response to an expose-event
    #__gsignals__ = { "draw": "override" }
    step = 0
    event_consumers = []
    active_event_consumer = None
    expose_called = True

    def __init__(self):
        Gtk.DrawingArea.__init__(self)
        self.create()

    def create(self):
        self.connect("button_press_event", self.button_press_event)
        self.connect("button_release_event", self.button_release_event)
        self.connect("motion_notify_event", self.motion_notify_event)
        self.connect("scroll_event", self.scroll_event)
        # self.connect("key_press_event", self.key_press_event)
        # self.connect("key_release_event", self.key_release_event)
        self.connect("draw", self.do_expose_event)
        self.set_events(Gdk.EventMask.KEY_PRESS_MASK | Gdk.EventMask.KEY_RELEASE_MASK)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.SCROLL_MASK)
        self.prev_scr_size = (-1,-1)
        self.cr = None
        self.cr_surf = None
        self.pangolayout = None

    def periodic(self):
        if (self.expose_called == False):
            return True
        ep.process()
        return True

    def screen_changed(self, w, h):
        self.cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.cr = cairo.Context(self.cr_surf)

        self.pangolayout = PangoCairo.create_layout(self.cr)
        self.pangolayout.set_font_description(Pango.font_description_from_string('Serif Normal 10'))
        self.pangolayout.set_alignment(Pango.Alignment.CENTER)
        self.prev_scr_size = (w,h)

    def save_project(self, *args):
        pass

    def update(self):
        self.expose_called = False
        self.queue_draw()

    def scroll_event(self, widget, event):
        if event.direction == Gdk.ScrollDirection.UP:
            ep.push_event(ee.scroll_up, (None))
        elif event.direction == Gdk.ScrollDirection.DOWN:
            ep.push_event(ee.scroll_down, (None))
    
    def button_press_event(self, widget, event):
        if event.button == 1:
            ep.push_event(ee.screen_left_press, (event.x, event.y))

    def key_press_event(self, widget, event):
        debug("key press:" + str(event.keyval))
        if event.keyval == Gdk.keyval_from_name('Escape'): # ESC
           ep.push_event(ee.escape, (None))

    def key_release_event(self, widget, event):
        debug("key release:" + str(event.keyval))
    
    def button_release_event(self, widget, event):
        if event.button == 1:
            ep.push_event(ee.screen_left_release, (event.x, event.y))

    def motion_notify_event(self, widget, event):
        ep.push_event(ee.pointer_motion, (event.x, event.y))

    # Handle the expose-event by drawing
    def do_expose_event(self, widget, cr_gdk):
        self.expose_called = True
        surface = cr_gdk.get_target()
        w = self.get_allocation().width#surface.get_width()
        h = self.get_allocation().height#surface.get_height()
        Singleton.state.set_screen_offset((w//2, h//2))
        offset = Singleton.state.get_offset()
        scale = Singleton.state.get_scale()
        if self.prev_scr_size!=(w,h):
            self.screen_changed(w,h)
        cr = self.cr
        cr_surf = self.cr_surf
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(0, 0, w, h)
        cr.clip()

        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        # coords start
        cr.translate(offset[0], offset[1])
        cr.set_source_rgb(0.6, 0.6, 0.6)
        cr.arc(0,0,10,0,2*math.pi)
        cr.stroke()
        cr.identity_matrix()
        
        step = self.calc_step((w,h))
        self.draw_grid_lines(cr, offset, step, (w,h))
        self.draw_cursor(cr)
        self.draw_grid_points(cr, offset, step, (w,h))

        self.draw_elements(cr)
        self.draw_current_element(cr)

        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

    def draw_current_element(self, cr):
        if (Singleton.ep.current_element == None):
            return
        Singleton.ep.current_element.draw(cr)
        cr.identity_matrix()

    def draw_elements(self, cr):
        for e in Singleton.state.elements:
            e.draw(cr)
        # if (Singleton.ep.current_element == None):
        #     return
        # Singleton.ep.current_element.draw(cr)
        # cr.identity_matrix()

    def calc_step(self, size):
        step = 1.0
        w,h=size
        xsteps = w/Singleton.state.scale[0]/step
        ysteps = h/Singleton.state.scale[1]/step
        maxsteps = max(xsteps, ysteps)
        mins = 40
        maxs = 80
        if (maxsteps < mins):
            while (maxsteps < mins):
                if (step//10 == 0):
                    break
                step//=10
                xsteps = w/Singleton.state.scale[0]/step
                ysteps = h/Singleton.state.scale[1]/step
                maxsteps = max(xsteps, ysteps)
        if (maxsteps > maxs):
            while (maxsteps > maxs):
                step*=10
                xsteps = w/Singleton.state.scale[0]/step
                ysteps = h/Singleton.state.scale[1]/step
                maxsteps = max(xsteps, ysteps)
        return step

    def draw_grid_lines(self, cr, offset, step, size):
        w,h=size
        x = (offset[0]/Singleton.state.scale[0])%(step)
        y = (offset[1]/Singleton.state.scale[1])%(step)
        Singleton.state.step = step
        cr.set_source_rgb(0.95, 0.95, 0.95)
        while (x*Singleton.state.scale[0]<w):
            if ((x-offset[0]/Singleton.state.scale[0])==0):
                cr.set_source_rgb(0.8,1.0,0.8)
            else:
                cr.set_source_rgb(0.95, 0.95, 0.95)
            cr.move_to(x*Singleton.state.scale[0],0)
            cr.line_to(x*Singleton.state.scale[0],h)
            cr.stroke()
            x += step

        y = (offset[1]/Singleton.state.scale[1])%(step)
        while (y*Singleton.state.scale[1]<h):
            if ((y-offset[1]/Singleton.state.scale[0])==0):
                cr.set_source_rgb(1.0,0.8,0.8)
            else:
                cr.set_source_rgb(0.95, 0.95, 0.95)

            cr.move_to(0, y*Singleton.state.scale[1])
            cr.line_to(w, y*Singleton.state.scale[1])
            cr.stroke()
            y += step

        cr.identity_matrix()


    def draw_cursor(self, cr):
        cr.set_source_rgb(0.7, 0.7, 0.7)
        cr.rectangle(ep.cursor_position[0]-3, ep.cursor_position[1]-3, 6, 6)
        cr.stroke()
        cr.identity_matrix()

        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.move_to(ep.cursor_position[0]-6, ep.cursor_position[1])
        cr.line_to(ep.cursor_position[0]+6, ep.cursor_position[1])
        cr.stroke()
        cr.move_to(ep.cursor_position[0], ep.cursor_position[1]-6)
        cr.line_to(ep.cursor_position[0], ep.cursor_position[1]+6)
        cr.stroke()
        cr.identity_matrix()
        self.pangolayout.set_markup('%.3f, %.3f'%(ep.pointer_position[0], ep.pointer_position[1]), -1)
        cr.move_to(ep.cursor_position[0]+12, ep.cursor_position[1]-6)
        PangoCairo.show_layout(cr, self.pangolayout)
        cr.identity_matrix()

    def draw_grid_points(self, cr, offset, step, size):
        w,h=size
        cr.set_source_rgb(0.1, 0.1, 0.1)
        x = (offset[0]/Singleton.state.scale[0])%(step)
        y = (offset[1]/Singleton.state.scale[1])%(step)
        Singleton.state.step = step
        while (x*Singleton.state.scale[0]<w):
            y = (offset[1]/Singleton.state.scale[1])%(step)
            while (y*Singleton.state.scale[1]<h):
                cr.rectangle(x*Singleton.state.scale[0]-1, y*Singleton.state.scale[1]-1, 2, 2)
                cr.fill()
                y += step
            x += step
        cr.identity_matrix()
