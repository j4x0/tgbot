import re

class AsyncEvent(object):
    def __init__(self, worker_pool):
        self.worker_pool = worker_pool
        self.handlers = []

    def __call__(self, callback):
        self.handlers.append((None, callback))

    def when(self, should_handle_fn, callback):
        self.handlers.append((should_handle_fn, callback))

    def emit(self, *args, **kwargs):
        for should_handle_fn, callback in self.handlers:
            if should_handle_fn == None or should_handle_fn(*args, **kwargs):
                self.worker_pool.apply(callback, args, kwargs)

class MessageEvent(AsyncEvent):
    def match(self, pattern, callback):
        self.when(lambda chat, user, message: re.match(pattern, message.text) != None, callback)

class CallbackQueryEvent(AsyncEvent):
    def datamatch(self, pattern, callback):
        self.when(lambda user, cq: re.match(pattern, cq.data) != None, callback)
