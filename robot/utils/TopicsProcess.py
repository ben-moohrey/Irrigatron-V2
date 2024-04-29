import multiprocessing

class Topic:
    def __init__(self, manager):
        # Using a managed dict to store the data, allowing multiple processes to access it safely
        self.data = manager.dict()
        self.data['value'] = None

    def write_data(self, value):
        # Writing data is non-blocking as manager.dict takes care of synchronization
        self.data['value'] = value

    def read_data(self):
        # Reading data is non-blocking as manager.dict takes care of synchronization
        
        return self.data['value']

class Topics:
    def __init__(self, topics_dict=None):
        if topics_dict is None:
            topics_dict = {}
        # Initialize a Manager to handle shared objects
        self.manager = multiprocessing.Manager()
        self.topics_dict = self.manager.dict()

        # Initialize topics and write initial data if any
        for k, v in topics_dict.items():
            topic = self.get_topic(k)
            topic.write_data(v)

    def get_topic(self, key):
        if key not in self.topics_dict:
            # Create a new Topic object with the shared manager
            self.topics_dict[key] = Topic(self.manager)
        return self.topics_dict[key]
