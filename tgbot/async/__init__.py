import threading

class Future(object):
    def __init__(self):
        self.finished = threading.Event()
        self.mutex = threading.Lock()

        self.retval = None
        self.callbacks = []

    def then(self, callback):
        if self.finished.is_set():
            callback(self.retval)
            return self
        self.mutex.acquire()
        self.callbacks.append(callback)
        self.mutex.release()
        return self

    def finalize(self, retval):
        # Atomic
        self.retval = retval

        self.mutex.acquire()
        for callback in self.callbacks:
            callback(retval)
        self.mutex.release()

        # Notify other threads
        self.finished.set()

    def err(self, exception):
        #TODO
        self.finished.set()

    def await(self):
        while True:
            if self.finished.wait(0.5):
                break
        return self.retval
