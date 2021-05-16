#!/usr/bin/env python

# Copyright 2009-2016 Thomas Paviot (tpaviot@gmail.com)
##
# This file is part of pythonOCC.
##
# pythonOCC is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# pythonOCC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import sys

from OCC import VERSION
from bcad.binterpreter.main_window import MainWindow
from bcad.binterpreter.singleton import Singleton

log = logging.getLogger(__name__)


def check_callable(_callable):
    if not callable(_callable):
        raise AssertionError("The function supplied is not callable")


def init_display(background_gradient_color1=None, background_gradient_color2=None, display_triedron=False, periodic_callback=None, period=None):

    win = MainWindow(False, Singleton.pipe, Singleton.img)
    print("Init driver")
    win.canva.init_driver()
    display = win.canva._display
    
    def start_display():
        win.mainloop()

    if display_triedron:
        display.display_triedron()

    if background_gradient_color1 and background_gradient_color2:
        display.set_bg_gradient_color(background_gradient_color1, background_gradient_color2)

    return display, start_display


if __name__ == '__main__':
    display, start_display = init_display()
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeBox

    def sphere(event=None):
        display.DisplayShape(BRepPrimAPI_MakeSphere(100).Shape(), update=True)

    def cube(event=None):
        display.DisplayShape(BRepPrimAPI_MakeBox(1, 1, 1).Shape(), update=True)

    def quit(event=None):
        sys.exit()

    start_display()
