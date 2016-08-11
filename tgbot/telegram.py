from os import path
import requests
import threading

from entities.dialogue import *
from entities.files import *

from async.workers import WorkerPool
from async.timed import Signaller

class APIException(Exception):
    def __init__(self, reason, request_url = None):
        self.reason = reason
        self.request_url = request_url

    def __str__(self):
        msg = ""
        if self.request_url != None: msg += "Error while fetching {0}:\n".format(self.request_url)
        msg += self.reason
        return msg

class BotAPI(object):
    ENDPOINT_URL = "https://api.telegram.org/bot{0}/{1}"
    DOWNLOAD_URL = "https://api.telegram.org/file/bot{0}/{1}"

    def __init__(self, token):
        self.token = token
        self.passed_api = None

    def request(self, method_name, method="post", params = {}):
        url = self.ENDPOINT_URL.format(self.token, method_name)
        payload = {}
        files = {}
        for k, v in params.iteritems():
            if v == None: continue
            if type(v) == file:
                files[k] = v
            else:
                payload[k] = v
        try:
            response = requests.request(method, url, params = payload, files = files, timeout = 600, headers = {"User-Agent": "tgbot"})
        finally:
            # Close all files
            for v in files.values():
                try:
                    v.close()
                except: pass
        try:
            data = response.json()
        except:
            raise APIException("Telegram returned invalid JSON", url)
        if not data["ok"]:
            raise APIException(data["description"] if "description" in data else "A Telegram API error occurred", url)
        return data

    def get_updates(self, **kwargs):
        return self.request("getUpdates", "post", kwargs)

    def set_webhook(self, **kwargs):
        return self.request("setWebhook", "post", kwargs)

    def remove_webhook(self):
        return self.set_webhook(url = "")

    def forward_message(self, pass_api = None, **kwargs):
        return Message.build(self.request("forwardMessage", "post", kwargs)["result"], self.passed_api)

    def send_message(self, pass_api = None, **kwargs):
        return Message.build(self.request("sendMessage", "post", kwargs)["result"], self.passed_api)

    def edit_message_text(self, pass_api = None, **kwargs):
        return Message.build(self.request("editMessageText", "post", kwargs)["result"], self.passed_api)

    def edit_message_caption(self, pass_api = None, **kwargs):
        return Message.build(self.request("editMessageCaption", "post", kwargs)["result"], self.passed_api)

    def edit_message_reply_markup(self, pass_api = None, **kwargs):
        return Message.build(self.request("editMessageReplyMarkup", "post", kwargs)["result"], self.passed_api)

    def send_photo(self, pass_api = None, **kwargs):
        return Message.build(self.request("sendPhoto", "post", kwargs)["result"], self.passed_api)

    def download_file(self, file_id, name):
        file_data = self.request("getFile", "post", {"file_id": file_id})["result"]
        if "file_path" not in file_data:
            raise APIException("File expired")

        parts = file_data["file_path"].split(".")
        ext = parts[-1] if len(parts) > 0 else ""
        target_path = name + "." + ext

        url = self.DOWNLOAD_URL.format(self.token, file_data["file_path"])
        response = requests.get(url, stream = True)
        with open(target_path, "wb") as fp:
            for chunk in response.iter_content(chunk_size = 1024):
                fp.write(chunk)
        response.close()

        return target_path

class LimitedBotAPI(BotAPI):
    REQUEST_SIGNAL = 0

    def __init__(self, token, requests_per_second = 5, messages_to_chat_per_second = 1):
        BotAPI.__init__(self, token)
        self.signaller = Signaller()
        self.signaller.add_signal(self.REQUEST_SIGNAL, 1. / requests_per_second)
        self._mstps = messages_to_chat_per_second

        self.mutex = threading.Lock()
        self.chat_signals_added = []

    def request(self, method_name, method = "post", params = {}):
        self.signaller.wait_for(self.REQUEST_SIGNAL)
        return BotAPI.request(self, method_name, method, params)

    def wait_till_chat_signal(self, chat_id):
        self.mutex.acquire()
        if chat_id not in self.chat_signals_added:
            self.signaller.add_signal(chat_id, self._mstps)
            self.chat_signals_added.append(chat_id)
        self.mutex.release()
        self.signaller.wait_for(chat_id)

    def send_message(self, pass_api = None, **kwargs):
        if "chat_id" not in kwargs:
            raise KeyError("'chat_id' was not passed to 'send_message'")
        self.wait_till_chat_signal(kwargs["chat_id"])
        return BotAPI.send_message(self, pass_api, **kwargs)

    def forward_message(self, pass_api = None, **kwargs):
        if "chat_id" not in kwargs:
            raise KeyError("'chat_id' was not passed to 'forward_message'")
        self.wait_till_chat_signal(kwargs["chat_id"])
        return BotAPI.forward_message(self, pass_api, **kwargs)

    def start(self):
        self.signaller.start()

    def stop(self):
        self.signaller.stop()

class AsyncifiedAPI(object):
    def __init__(self, api, worker_pool):
        self.worker_pool = worker_pool
        self._api = api
        self.token = self._api.token
        self._api.passed_api = self #Pass this object as API to the instantiated entities

    def underlying_api(self):
        return self._api

    def __getattr__(self, key):
        if not hasattr(self._api, key): raise NameError()
        return self.worker_pool.asyncify(getattr(self._api, key))
