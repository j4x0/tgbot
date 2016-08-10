import threading
from time import sleep, time
import Queue

class TimeoutException(Exception):
    pass

class Signaller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.do_run = False

        self.mutex = threading.Lock()
        self.intervals = {}
        self.states = {}
        self.min_interval = 1

        self.outgoing_mutex = threading.Lock()
        self.outgoing = []

    def add_signal(self, signal, interval):
        self.mutex.acquire()
        self.intervals[signal] = interval
        self.states[signal] = 0
        if self.min_interval > interval:
            self.min_interval = interval
        self.mutex.release()

    def has_signal(self, signal):
        self.mutex.acquire()
        has_signal = signal in self.intervals.keys()
        self.mutex.release()
        return has_signal

    def _do_send(self, signal, interval, dt):
        self.states[signal] += dt
        if self.states[signal] >= interval:
            self.states[signal] = 0
            return True
        else: return False

    def _send_signals(self, signals):
        self.outgoing_mutex.acquire()
        for signal in signals:
            if signal not in self.outgoing:
                self.outgoing.append(signal)
        self.outgoing_mutex.release()

    def run(self):
        t = time()
        dt = 100
        while self.do_run:
            if dt < self.min_interval:
                sleep(self.min_interval - dt)

            self.mutex.acquire()
            dt = time() - t
            signals = []
            for signal, interval in self.intervals.iteritems():
                if self._do_send(signal, interval, dt):
                    signals.append(signal)
            self.mutex.release()

            t = time()
            self._send_signals(signals)

    def wait_for(self, signal):
        while True:
            try:
                self.outgoing_mutex.acquire()
                index = self.outgoing.index(signal)
                del self.outgoing[index]
                return
            except:
                pass
            finally:
                self.outgoing_mutex.release()
            sleep(0.005) # 5ms delay by default

    def start(self):
        self.do_run = True
        return threading.Thread.start(self)

    def stop(self):
        self.do_run = False
