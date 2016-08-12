import threading
import Queue

from tgbot import logging
from tgbot.async import Future

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
                fn, future, args, kwargs = self.q.get(True, 0.5)
            except Queue.Empty: continue
            try:
                retval = fn(*args, **kwargs)
                future.finalize(retval)
            except Exception as e:
                logging.error(str(type(e)) + " inside worker thread:\n" + str(e))
                future.err(e)

    def stop(self):
        self.do_run = False

class WorkerPool(object):
    def __init__(self, count):
        self.q = Queue.Queue()
        self.workers = [Worker(self.q) for i in range(count - 1)]

    def apply(self, fn, args = [], kwargs = {}):
        future = Future()
        self.q.put((fn, future, args, kwargs))
        return future

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
