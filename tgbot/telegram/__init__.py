import requests
from entities import *
from bot.workers import WorkerPool

class APIException(Exception):
    def __init__(self, reason, request_url = None):
        self.reason = reason
        self.request_url = request_url

    def __str__(self):
        msg = ""
        if self.request_url != None: msg += "Error while fetching {0}".format(self.request_url)
        msg += "\n"
        msg += self.reason
        return msg


class BotAPI(object):
    ENDPOINT_URL = "https://api.telegram.org/bot{0}/{1}"

    def __init__(self, token):
        self.token = token

    def request(self, method_name, method="get", payload = {}):
        url = self.ENDPOINT_URL.format(self.token, method_name)
        response = requests.request(method, url, data = payload, timeout = 600)
        if response.status_code != 200:
            raise APIException("Telegram couldn't handle the request", url)
        try:
            data = response.json()
        except:
            raise APIException("Telegram returned invalid JSON", url)
        return data

    def get_updates(self, **kwargs):
        data = self.request("getUpdates", "post", kwargs)
        return [Update.deserialize(item) for item in data["result"]]

    def send_message(self, **kwargs):
        return self.request("sendMessage", "post", kwargs)

class AsyncBotAPI(object):
    def __init__(self, token, worker_pool):
        self.worker_pool = worker_pool
        self.token = token
        self._api = BotAPI(token)

    def __getattr__(self, name):
        if not hasattr(self._api, name): raise NameError("'AsyncBotAPI' has no attribute '" + name + "'")
        fn = getattr(self._api, name)
        def async_wrap(callback = None, *args, **kwargs):
            def callee(*args, **kwargs):
                retval = fn(*args, **kwargs)
                if callback != None: callback(retval)
            return self.worker_pool.apply(callee, args, kwargs)
        return async_wrap
