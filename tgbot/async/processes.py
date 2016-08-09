import multiprocessing
import time
import signal

from tgbot import logging
from tgbot.telegram import BotAPI

class ReceiveProcess(multiprocessing.Process):
    def __init__(self, token, q):
        multiprocessing.Process.__init__(self)
        self.q = q
        self.api = BotAPI(token)
        self.daemon = True
        self.offset = None

    def fetch_updates(self):
        logging.log("Fetching updates")
        response = self.api.get_updates(offset = self.offset, timeout = 120) if self.offset != None else self.api.get_updates(timeout = 120)
        updates = response["result"]
        if len(updates) > 0:
            self.offset = updates[len(updates) - 1]["update_id"] + 1
        for update in updates: self.q.put(update)

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN) # Make sure KeyboardInterrupts are not sent to this process
        try:
            while True:
                self.fetch_updates()
        except Exception as e:
            logging.error("An exception occurred inside recv process:\n" + str(e))
        finally:
            self.q.put(None)
