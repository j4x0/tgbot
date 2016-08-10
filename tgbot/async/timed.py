import threading
import time
import Queue

class TimedSignaller(threading.Thread):
    def __init__(self, interval):
        threading.Thread.__init__(self)
        self._interval = interval
        self.do_run = True
        self.signal_queue = Queue.Queue(maxsize  = 1)

    def run(self):
        while self.do_run:
            time.sleep(self._interval)
            try:
                self.signal_queue.put(1, False) # Signal one thread
            except:
                pass

    def wait(self):
        while True:
            try:
                self.signal_queue.get(True, 0.5) # Get the signal & return
                break
            except:
                pass
            if not self.do_run:
                raise Exception("Signaller was stopped")

    def start(self):
        self.do_run = True
        threading.Thread.start(self)

    def stop(self):
        self.do_run = False
