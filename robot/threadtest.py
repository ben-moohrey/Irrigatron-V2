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
    def __init__(self):
        self.topics_dict = {}
    
    def get_topic(self, key):
        if key not in self.topics_dict:
            self.topics_dict[key] = Topic()
        return self.topics_dict[key]

class BaseModule:
    def __init__(self, topics: Topics, thread_id: int):
        self.topics = topics
        self.thread_id = thread_id

    def run(self):
        raise NotImplementedError
    
    @classmethod
    def spawn(cls, topics, shutdown_flag, thread_id):
        module = cls(topics, thread_id)
        while not shutdown_flag.is_set():
            module.run()


class WifiModule(BaseModule):
    def __init__(self, topics, thread_ids):
        super().__init__(topics, thread_ids)
        self.main_topic = self.topics.get_topic("test_topic")
        self.i = 0

    def run(self):
        self.main_topic.write_data(self.i)
        self.topics.get_topic("test_topic").write_data(self.i)
        self.i += 1

def main():
    topics = Topics()
    threads = []
    shutdown_flag = threading.Event()

    # Create and start subthreads
    modules = [
        WifiModule,
    ]

    for i in range(0, len(modules)):
        thread = threading.Thread(target=modules[i].spawn, args=(topics, shutdown_flag, i))
        thread.start()
        threads.append(thread)
    
    try:
        while (True):
            print(topics.get_topic("test_topic").read_data())

    except KeyboardInterrupt:
        shutdown_flag.set()
        print("Shutting Down Gracefully")

    for thread in threads:
        thread.join()

    print("Successfully Shutdown")

if __name__ == "__main__":
    main()



# class Inner:
#     def __init__(self, outer):
#         self.haha = 1

#     def test(self):
#         print()

#     def run(self):
#         print()

#     def spawn(self, outer):
#         runner = self(outer)
#         return_val = 0
#         while(return_val == 0):
#             running = self.run()
#         return running




