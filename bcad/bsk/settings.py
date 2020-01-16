from __future__ import absolute_import, division, print_function

class Settings(object):
    def __init__(self, data=None):
        if data == None:
            self.centerpoint_snap = True
        else:
            self.deserialize(data)

    def is_centerpoint_snap_enabled(self):
        return self.centerpoint_snap

    def serialize(self):
        return {"type": "settings", "centerpoint_snap": self.centerpoint_snap}

    def deserialize(self, data):
        self.centerpoint_snap = data["centerpoint_snap"]
