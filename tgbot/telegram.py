import requests

from async.workers import WorkerPool

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

    def __init__(self, token):
        self.token = token

    def request(self, method_name, method="post", params = {}):
        url = self.ENDPOINT_URL.format(self.token, method_name)
        payload = {}
        for k, v in params.iteritems():
            if v != None: payload[k] = v
        response = requests.request(method, url, data = payload, timeout = 600)
        try:
            data = response.json()
        except:
            raise APIException("Telegram returned invalid JSON", url)
        if not data["ok"]:
            raise APIException(data["description"] if "description" in data else "A Telegram API error occurred", url)
        return data

    def get_updates(self, **kwargs):
        return self.request("getUpdates", "post", kwargs)

    def send_message(self, **kwargs):
        return self.request("sendMessage", "post", kwargs)

class AsyncBotAPI(BotAPI):
    def __init__(self, token, worker_pool):
        self.worker_pool = worker_pool
        BotAPI.__init__(self, token)

    def async_requester(self, method_name, method, params, callback):
        retval = BotAPI.request(self, method_name, method, params)
        if callback != None: callback(retval)

    def request(self, method_name, method = "post", params = {}):
        callback = params["callback"] if "callback" in params else None
        async = params["async"] if "async" in params else True
        del params["callback"]
        del params["async"]
        if async:
            self.worker_pool.apply(self.async_requester, [method_name, method, params, callback])
        else:
            return BotAPI.request(self, method_name, method, params)
