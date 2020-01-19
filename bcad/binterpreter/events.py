from logging import debug, info, warning, error, critical
import logging

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import pyinotify

from bcad.binterpreter.singleton import Singleton

mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY  # watched events

class WatchdogHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        debug("Received created event - %s." % event.pathname)

    def process_IN_DELETE(self, event):
        debug("Received deleted event - %s." % event.pathname)

    def process_IN_MODIFY(self, event):
        debug("Received modified event - %s." % event.pathname)
        if (event.pathname == Singleton.root_file):
            info("Reloading root file")
        else:
            info("Reloading subfile")
        Singleton.sd.reset()
        Singleton.scl.reload_file()

class EVEnum(object):
    main_start = "main_start"
    init_display = "init_display"
    parse_file = "parse_file"

class EventProcessor(object):
    ee = EVEnum()
    event_list = []
    selected_elements = []
    selected_path = None
    selected_tool_operation = None
    left_press_start = None
    pointer_position = None
    shift_pressed = False
    ctrl_pressed = False
    started = False

    def __init__(self):
        Singleton.ee = self.ee
        Singleton.ep = self
        self.started = False
        self.events = {
            self.ee.main_start: [self.main_start],
            self.ee.init_display: [self.init_display],
            self.ee.parse_file: [self.parse_file],
        }

    def reset(self):
        self.selected_elements = []
        self.selected_path = None
        self.selected_tool_operation = None
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
        if self.started == True:
            Singleton.notifier.process_events()
            while Singleton.notifier.check_events():  #loop in case more events appear while we are processing
                Singleton.notifier.read_events()
                Singleton.notifier.process_events()
        #     self.push_event(self.ee.main_start, None)
        #     self.started = True
        event_list = self.event_list[:]
        self.event_list = []
        for e, args in event_list:
            if e in self.events:
                for p in self.events[e]:
                    r = p(args)
                    if (r == False):
                        break
            else:
                dbgfname()
                warning("  Unknown event:"+str(e)+" args: "+str(args))
                warning("  Please report")

    def main_start(self, args):
        if self.started == False:
            self.started = True
            info("Starting")
            info(args)
            args = args[0]
            Singleton.observers = {}
            Singleton.root_file = args.file
            Singleton.wm = pyinotify.WatchManager()
            Singleton.handler = WatchdogHandler()
            Singleton.notifier = pyinotify.Notifier(Singleton.wm, Singleton.handler, timeout=10)
            Singleton.observers[args.file] = Singleton.wm.add_watch(args.file, mask, rec=False)

            info("args: %s"%(str(args),))
            Singleton.scl.load_file()
        else:
            warning("Already started")

    def init_display(self, args):
        info("Init display")
        from bcad.binterpreter.scl_context import SCLDisplay
        Singleton.sd = SCLDisplay()

    def parse_file(self, args):
        path = args[0]
        info("Parse file %s"%(path,))
        if path in Singleton.observers:
            debug("path already observed")
        else:
            debug("starting path observer")
            Singleton.observers[path] = Singleton.wm.add_watch(path, mask, rec=False)

ee = EVEnum()
ep = EventProcessor()
