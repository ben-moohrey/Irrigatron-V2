import threading

class Topic:
    def __init__(self):
        self.data = None
        self.lock = threading.Lock()

    def write_data(self, value):
        with self.lock:
            self.data = value

    def read_data(self):
        with self.lock:
            return self.data

class Topics:
    def __init__(self, topics_dict={}):
        self.topics_dict = {}
        
        for k, v in topics_dict.items():
            self.get_topic(k).write_data(v)

    
    def get_topic(self, key):
        if key not in self.topics_dict:
            self.topics_dict[key] = Topic()
        return self.topics_dict[key]
    