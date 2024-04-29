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

def writer(topic, value):
    print(f"Process {multiprocessing.current_process().name} writing to topic")
    topic.write_data(value)
    print(f"Process {multiprocessing.current_process().name} wrote {value}")

def reader(topic):
    print(f"Process {multiprocessing.current_process().name} reading from topic")
    data = topic.read_data()
    print(f"Process {multiprocessing.current_process().name} read {data}")

def test_topics():
    topics = Topics()

    # Retrieve topics
    topic1 = topics.get_topic('topic1')
    topic2 = topics.get_topic('topic2')

    # Start processes to write to topics
    #p1 = multiprocessing.Process(target=writer, args=(topic1, 'Hello from topic1'))
    #p2 = multiprocessing.Process(target=writer, args=(topic2, 'Hello from topic2'))

    # Start processes to read from topics
    p3 = multiprocessing.Process(target=reader, args=(topic1,))
    p4 = multiprocessing.Process(target=reader, args=(topic2,))

    # Start all processes
    #p1.start()
    #p2.start()
    p3.start()
    p4.start()

    # Wait for all processes to complete
    #p1.join()
    #p2.join()
    p3.join()
    p4.join()

if __name__ == '__main__':
    test_topics()