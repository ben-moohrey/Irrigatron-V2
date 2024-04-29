from utils.TopicsProcess import Topics
import logging
class BaseModule:
    def __init__(self, topics: Topics, thread_id: int, settings: dict):
        self.topics = topics
        self.thread_id = thread_id
        self.settings = settings
        self.__STARTUP_TIME_T__ = topics.get_topic('__STARTUP_TIME__')

    def log(self, *msgs):
        print(f'[{self.thread_id}] > ', *msgs)

    def run(self, shutdown_flag):
        raise NotImplementedError
    
    def shutdown(self):
        raise NotImplementedError
    
    def __del__(self):
        self.shutdown()
        self.log('Shutdown Successfully')

    @classmethod
    def spawn(cls, shutdown_flag, topics, thread_id, settings, args):
        module = cls(topics, thread_id, settings, *args)
        while not shutdown_flag.is_set():
            module.run(shutdown_flag)

        
