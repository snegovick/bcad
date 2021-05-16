import json

RQ_LOAD_IMAGE     = 'load_image'
RQ_START_ROTATION = 'start_rotation'
RQ_ROTATE         = 'rotate'
RQ_SET_SIZE       = 'set_size'
RQ_STOP           = 'stop'
RQ_SCROLL         = 'scroll'
RQ_MOVE           = 'move'
RQ_PAN            = 'pan'

requests = {
    RQ_LOAD_IMAGE    : 1,
    RQ_START_ROTATION: 2,
    RQ_ROTATE        : 3,
    RQ_SET_SIZE      : 4,
    RQ_STOP          : 5,
    RQ_SCROLL        : 6,
    RQ_MOVE          : 7,
    RQ_PAN           : 8,
}

RP_IMAGE_DATA = 'image_data'
RP_ACK        = 'ack'

replies = {
    RP_IMAGE_DATA: 1,
    RP_ACK:        2,
}

class rqItem:
    def __init__(self, rq, args, retransmit=True):
        self.retransmit = retransmit
        self.request = json.dumps({'rq': requests[rq], 'args': args})

    def send(self, viewer):
        if viewer.is_waiting_reply():
            if self.retransmit == False:
                return True
            return False
        if (viewer.send_rq(self.request) == False):
            if (self.retransmit == True):
                return False
        return True

class rqQueue:
    def __init__(self):
        self.q = []

    def push_back(self, rqi):
        self.q.append(rqi)

    def pop_front(self):
        if len(self.q)>1:
            self.q = self.q[1:]
        else:
            self.q = []

    def process(self, viewer):
        if len(self.q)>0:
            current_rq = self.q[0]
            if current_rq.send(viewer) == True:
                self.pop_front()

    def rq_start_rotation(self, x, y):
        self.push_back(rqItem(RQ_START_ROTATION, [x, y], False))

    def rq_rotate(self, x, y):
        self.push_back(rqItem(RQ_ROTATE, [x, y], False))

    def rq_load_image(self):
        self.push_back(rqItem(RQ_LOAD_IMAGE, None, False))

    def rq_set_size(self, w, h):
        self.push_back(rqItem(RQ_SET_SIZE, [w, h], False))

    def rq_scroll(self, delta):
        self.push_back(rqItem(RQ_SCROLL, delta, False))

    def rq_move(self, x, y):
        self.push_back(rqItem(RQ_MOVE, [x, y], False))

    def rq_pan(self, x, y):
        print("rq pan", x, y)
        self.push_back(rqItem(RQ_PAN, [x, y], False))
