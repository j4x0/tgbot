import telegram
import multiprocessing
import threading
import Queue
import math

from processes import *
from workers import WorkerPool
import events
import logging

class Bot(object):
    def __init__(self, token):
        self.token = token

        self.events_worker_pool = WorkerPool(20)
        self.api_worker_pool = WorkerPool(20)

        self.api = telegram.AsyncBotAPI(token, self.api_worker_pool)

        self.on_message = events.MessageEvent(self.events_worker_pool)

        self.updates = multiprocessing.Queue()
        self.receiver = ReceiveProcess(token, self.updates)


    def process_update(self, update):
        if update.message != None:
            self.on_message.emit(update.message)

    def process_updates(self):
        while True:
            try:
                update = self.updates.get(True, 5)
            except Queue.Empty:
                continue
            if update == None: break # Receive process sent stop signal
            self.process_update(update)

    def start(self):
        logging.info("Bot is starting")
        self.receiver.start()
        self.events_worker_pool.start()
        self.api_worker_pool.start()
        try:
            self.process_updates()
        except KeyboardInterrupt: pass
        finally:
            self.stop()

    def stop(self):
        logging.info("Bot is stopping")
        self.receiver.terminate()
        self.receiver.join()
        self.events_worker_pool.stop()
        self.api_worker_pool.stop()
