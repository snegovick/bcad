#!/usr/bin/env python3
import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from gi.repository import GObject as gobject

from logging import debug, info, warning, error, critical
import logging

from bsuite.bsk.events import EVEnum, EventProcessor, ee, ep
from bsuite.bsk.cairo_screen import CairoScreen
from bsuite.bsk.singleton import Singleton
from bsuite.bsk.project import project
from bsuite.bsk.util import dbgfname
from bsuite.bsk import util

class Handler:
    def onDestroy(self, *args):
        Gtk.main_quit()

class SketcherApp:
    def __init__(self, argv):
        args = {"--verbose": {"is_set": util.NOT_SET, "has_option": util.HAS_OPTION, "option": None},
                "--plugins-dir": {"is_set": util.NOT_SET, "has_option": util.HAS_OPTION, "option": None}}
        util.parse_args(args, argv)
        if args["--verbose"]["has_option"]:
            verbose_level = int(args["--verbose"]["option"])
            if verbose_level == 1:
                logging.getLogger("").setLevel(logging.CRITICAL)
            elif verbose_level == 2:
                logging.getLogger("").setLevel(logging.ERROR)
            elif verbose_level == 3:
                logging.getLogger("").setLevel(logging.WARNING)
            elif verbose_level == 4:
                logging.getLogger("").setLevel(logging.INFO)
            elif verbose_level >= 5:
                logging.getLogger("").setLevel(logging.DEBUG)

        self.window = Gtk.Window()
        self.window.maximize()
        self.window.connect("delete-event", Gtk.main_quit)

        self.window.set_events(Gdk.EventMask.KEY_PRESS_MASK | Gdk.EventMask.KEY_RELEASE_MASK)
        self.window.connect("key_press_event", self.key_press_event)
        self.window.connect("key_release_event", self.key_release_event)


        self.menu_bar = Gtk.MenuBar()
        agr = Gtk.AccelGroup()
        self.window.add_accel_group(agr)
        self.mk_file_menu(agr)
        self.mk_edit_menu(agr)

        self.window_vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self.window_vbox.pack_start(self.menu_bar, expand=False, fill=False, padding=0)
        
        self.window.add(self.window_vbox)

        self.widget = CairoScreen()

        self.__mk_left_vbox()
        self.hbox = Gtk.HBox(homogeneous=False, spacing=0)
        self.hbox.pack_start(self.left_vbox, expand=False, fill=False, padding=0)

        self.widget_vbox = Gtk.VBox(homogeneous=False, spacing=0)

        self.operations_hbox = Gtk.HBox(homogeneous=False, spacing=0)
        self.operations_bar = Gtk.MenuBar()
        self.operations_hbox.pack_start(self.operations_bar, expand=False, fill=False, padding=0)
        self.mk_line_menu(agr)
        self.mk_circle_menu(agr)
        self.mk_rectangle_menu(agr)
        
        hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.operations_hbox.pack_start(hseparator, expand=False, fill=False, padding=0)
        self.snap_bar = Gtk.MenuBar()
        self.mk_snap_menu(agr)

        self.widget_vbox.pack_start(self.operations_hbox, expand=False, fill=False, padding=0)
        self.widget_vbox.pack_start(self.widget, expand=True, fill=True, padding=0)
        
        self.hbox.pack_start(self.widget_vbox, expand=True, fill=True, padding=0)

        self.window_vbox.pack_start(self.hbox, expand=True, fill=True, padding=0)
        
        self.window.show_all()
        self.window.present()
        ep.push_event(ee.sketcher_start, (None))
        Singleton.mw = self
        ep.mw = self
        gobject.timeout_add(10, self.widget.periodic)
        Gtk.main()

    def mk_file_menu(self, agr):
        self.file_menu = Gtk.Menu()
        self.file_item = Gtk.MenuItem.new_with_mnemonic(label="_File")
        self.file_item.set_submenu(self.file_menu)
        self.menu_bar.append(self.file_item)

        self.new_project_item = Gtk.MenuItem(label="New sketch")
        key, mod = Gtk.accelerator_parse("<Control>N")
        self.new_project_item.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)

        self.open_project_item = Gtk.MenuItem(label="Open sketch ...")
        key, mod = Gtk.accelerator_parse("<Control>O")
        self.open_project_item.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)

        self.save_project_item = Gtk.MenuItem(label="Save sketch")
        key, mod = Gtk.accelerator_parse("<Control>S")
        self.save_project_item.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)

        self.save_project_as_item = Gtk.MenuItem(label="Save sketch as ...")
        key, mod = Gtk.accelerator_parse("<Control><Shift>S")
        self.save_project_as_item.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)

        sep_export_import = Gtk.SeparatorMenuItem()
        self.export_item = Gtk.MenuItem(label="Export ...")
        self.import_item = Gtk.MenuItem(label="Import ...")
        sep_quit = Gtk.SeparatorMenuItem()
        self.quit_item = Gtk.MenuItem(label="Quit")
        key, mod = Gtk.accelerator_parse("<Control>Q")
        self.quit_item.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)

        self.file_menu.append(self.new_project_item)
        self.file_menu.append(self.open_project_item)
        self.file_menu.append(self.save_project_item)
        self.file_menu.append(self.save_project_as_item)
        self.file_menu.append(sep_export_import)
        self.file_menu.append(self.import_item)
        self.file_menu.append(self.export_item)
        self.file_menu.append(sep_quit)
        self.file_menu.append(self.quit_item)

        # self.import_item.connect("activate", lambda *args: ep.push_event(ee.load_click, args))
        # self.export_item.connect("activate", lambda *args: ep.push_event(ee.save_click, args))
        # self.new_project_item.connect("activate", lambda *args: ep.push_event(ee.new_project_click, args))
        # self.open_project_item.connect("activate", lambda *args: ep.push_event(ee.load_project_click, args))
        # self.save_project_item.connect("activate", lambda *args: ep.push_event(ee.save_project_click, args))
        # self.save_project_as_item.connect("activate", lambda *args: ep.push_event(ee.save_project_as_click, args))
        # self.quit_item.connect("activate", lambda *args: ep.push_event(ee.quit_click, args))

    def mk_edit_menu(self, agr):
        self.edit_menu = Gtk.Menu()
        self.edit_item = Gtk.MenuItem.new_with_mnemonic(label="_Edit")
        self.edit_item.set_submenu(self.edit_menu)
        self.menu_bar.append(self.edit_item)

        self.undo_item = Gtk.MenuItem(label="Undo")
        key, mod = Gtk.accelerator_parse("<Control>Z")
        self.undo_item.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)

        self.redo_item = Gtk.MenuItem(label="Redo")
        key, mod = Gtk.accelerator_parse("<Control>Y")
        self.redo_item.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)

        sep_undo_redo = Gtk.SeparatorMenuItem()

        self.edit_menu.append(sep_undo_redo)
        self.edit_menu.append(self.undo_item)
        self.edit_menu.append(self.redo_item)

        # self.undo_item.connect("activate", lambda *args: ep.push_event(ee.undo_click, args))
        # self.redo_item.connect("activate", lambda *args: ep.push_event(ee.redo_click, args))

    def mk_line_menu(self, agr):
        self.line_item = Gtk.MenuItem.new_with_mnemonic(label="_Line")
        self.operations_bar.append(self.line_item)
        self.line_menu = Gtk.Menu()
        self.line_item.set_submenu(self.line_menu)
        
        self.line_2point_item = Gtk.MenuItem(label="Two point line")
        self.line_2point_item.connect("activate", lambda *args: ep.push_event(ee.line_2point_click, args))

        self.line_menu.append(self.line_2point_item)

    def mk_circle_menu(self, agr):
        self.circle_item = Gtk.MenuItem.new_with_mnemonic(label="_Circle")
        self.operations_bar.append(self.circle_item)

    def mk_rectangle_menu(self, agr):
        self.rectangle_item = Gtk.MenuItem.new_with_mnemonic(label="_Rectangle")
        self.operations_bar.append(self.rectangle_item)

    def mk_rectangle_menu(self, agr):
        self.rectangle_item = Gtk.MenuItem.new_with_mnemonic(label="_Rectangle")
        self.operations_bar.append(self.rectangle_item)

    def mk_snap_menu(self, agr):
        self.grid_item = Gtk.MenuItem.new_with_mnemonic(label="_Grid")
        self.snap_bar.append(self.grid_item)

    def __mk_left_vbox(self):
        self.left_vbox = Gtk.VBox(homogeneous=False, spacing=0)
        self.paths_label = Gtk.Label(label="Paths")
        self.scrolled_window = Gtk.ScrolledWindow()
        self.left_vbox.pack_start(self.paths_label, expand=False, fill=False, padding=0)

    def key_press_event(self, widget, event):
        debug("key press:" + str(event.keyval))
        self.widget.key_press_event(widget, event)

    def key_release_event(self, widget, event):
        debug("key release:" + str(event.keyval))
        self.widget.key_release_event(widget, event)

if __name__ == "__main__":
    SketcherApp(sys.argv)
