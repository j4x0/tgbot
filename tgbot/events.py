import re

class AsyncEvent(object):
    def __init__(self, worker_pool):
        self.worker_pool = worker_pool
        self.handlers = []

    def subscribe(self, should_handle_fn, callback):
        self.handlers.append((should_handle_fn, callback))

    def emit(self, *args, **kwargs):
        for should_handle_fn, callback in self.handlers:
            if should_handle_fn(*args, **kwargs):
                self.worker_pool.apply(callback, args, kwargs)

class MessageEvent(AsyncEvent):
    def match(self, pattern, callback):
        self.subscribe(lambda chat, user, message: True, callback) #message.text != None and re.match(pattern, message.text) != None, callback)
