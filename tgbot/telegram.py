import requests
import dialogue

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

    def forward_message(self, pass_api = None, **kwargs):
        return dialogue.Message.build(self.request("forwardMessage", "post", kwargs)["result"], pass_api if pass_api != None else pass_api)

    def send_message(self, pass_api = None, **kwargs):
        return dialogue.Message.build(self.request("sendMessage", "post", kwargs)["result"], pass_api if pass_api != None else pass_api)

    def edit_message_text(self, pass_api = None, **kwargs):
        return dialogue.Message.build(self.request("editMessageText", "post", kwargs)["result"], pass_api if pass_api != None else pass_api)

    def edit_message_caption(self, pass_api = None, **kwargs):
        return dialogue.Message.build(self.request("editMessageCaption", "post", kwargs)["result"], pass_api if pass_api != None else pass_api)

    def edit_message_reply_markup(self, pass_api = None, **kwargs):
        return dialogue.Message.build(self.request("editMessageReplyMarkup", "post", kwargs)["result"], pass_api if pass_api != None else pass_api)


class AsyncBotAPI(object):
    def __init__(self, token, worker_pool):
        self.token = token
        self.worker_pool = worker_pool
        self._api = BotAPI(token)


    def __getattr__(self, key):
        if not hasattr(self._api, key): raise NameError()
        return self.worker_pool.asyncify(getattr(self._api, key), pass_api = self)
