import threading
import Queue
import logging

class Worker(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q
        self.do_run = True

    def run(self):
        while self.do_run:
            try:
                fn, args, kwargs = self.q.get(True, 0.5)
            except Queue.Empty: continue
            try:
                fn(*args, **kwargs)
            except Exception as e:
                logging.error("Exception inside worker thread:\n\t" + str(e))

    def stop(self):
        self.do_run = False

class WorkerPool(object):
    def __init__(self, count):
        self.q = Queue.Queue()
        self.workers = [Worker(self.q) for i in range(count - 1)]

    def apply(self, fn, args, kwargs):
        self.q.put((fn, args, kwargs))

    def start(self):
        for worker in self.workers:
            worker.start()

    def stop(self):
        for worker in self.workers:
            worker.stop()
        for worker in self.workers:
            worker.join()
