import time
class MoveTimer:
    def __init__(self, end):
        self.start = time.time()
        self.end = end

    def update(self):

        


class MoveTimers:
    def __init__(self):
        self.start = time.time()
        self.timers = []

    
    def update(self):
        for t in timers:
            t.update() 
    