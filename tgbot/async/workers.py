import threading
import Queue

from tgbot import logging

class Promise(object):
    def __init__(self):
        self.condition = threading.Condition()
        self.retval = None
        self.finished = False

        self.callbacks_lock = threading.Lock()
        self.callbacks = []

    def acquire(self):
        self.condition.acquire()

    def then(self, callback):
        if self.finished:
            callback(self.retval)
        self.callbacks_lock.acquire()
        self.callbacks.append(callback)
        self.callbacks_lock.release()
        return self

    def finalize(self, retval):
        self.finished = True
        self.retval = retval

        self.callbacks_lock.acquire()
        for callback in self.callbacks:
            callback(retval)
        self.callbacks_lock.release()

        # Notify other threads
        self.condition.notify_all()
        self.condition.release()

    def err(self, exception):
        self.condition.notify_all()
        self.condition.release()

    def await(self):
        self.acquire()
        self.condition.wait() #when notified & lock released
        return self.retval

class Worker(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q
        self.do_run = True

    def start(self):
        self.do_run = True
        threading.Thread.start(self)

    def run(self):
        while self.do_run:
            try:
                fn, p, args, kwargs = self.q.get(True, 0.5)
            except Queue.Empty: continue
            try:
                p.acquire()
                retval = fn(*args, **kwargs)
                p.finalize(retval)
            except Exception as e:
                logging.error("Exception inside worker thread:\n" + str(e))
                p.err(e)

    def stop(self):
        self.do_run = False

class WorkerPool(object):
    def __init__(self, count):
        self.q = Queue.Queue()
        self.workers = [Worker(self.q) for i in range(count - 1)]

    def apply(self, fn, args = [], kwargs = {}):
        p = Promise()
        self.q.put((fn, p, args, kwargs))
        return p

    def asyncify(self, fn, **override_kwargs):
        def async_applier(*args, **kwargs):
            kwargs.update(override_kwargs)
            return self.apply(fn, args, kwargs)
        return async_applier

    def start(self):
        for worker in self.workers:
            worker.start()

    def stop(self):
        for worker in self.workers:
            worker.stop()
        for worker in self.workers:
            worker.join()
