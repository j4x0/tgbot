from tgbot.entities import RequestingEntity
from tgbot.entities.dialogue import Message

class CallbackQuery(RequestingEntity):
    def __init__(self, api):
        RequestingEntity.__init__(self, {
            "id":                   ("id", None),
            "inline_message_id":    ("inline_message_id", None),
            "data":                 ("data", "")
        }, api)

    def answer(self, text = None, show_alert = False):
        if self.api == None or self.id == None: raise Exception("This callback cannot be answered")
        self.api.answer_callback_query(
            callback_query_id = self.id,
            text = text,
            show_alert = show_alert)

    def _set_props(self, values = {}):
        RequestingEntity._set_props(self, values)
        self.message = Message.build(values["message"], self.api) if "message" in values else None
