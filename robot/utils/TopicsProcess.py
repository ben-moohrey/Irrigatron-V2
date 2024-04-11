from multiprocessing import Manager, Lock

class Topic:
    def __init__(self, manager):
        self.data = manager.Value('i', 0)  # example with an integer
        self.lock = Lock()

    def write_data(self, value):
        with self.lock:
            self.data.value = value

    def read_data(self):
        with self.lock:
            return self.data.value

class Topics:
    def __init__(self, topics_dict={}):
        self.manager = Manager()
        self.topics_dict = self.manager.dict()
        
        for k, v in topics_dict.items():
            self.get_topic(k).write_data(v)

    def get_topic(self, key):
        if key not in self.topics_dict:
            self.topics_dict[key] = Topic(self.manager)
        return self.topics_dict[key]