import utils

class TgEntity(object):
    def __init__(self, props):
        self._props = props
        self._set_props()

    def _set_props(self, values = {}):
        for prop_name, (field_name, default_value) in self._props.iteritems():
            value = values[field_name] if field_name in values else default_value
            setattr(self, prop_name, value)

    def update_properties(self, values):
        self._set_props(values)

    @classmethod
    def build(cls, data):
        entity = cls()
        entity._set_props(data)
        return entity

class Chat(TgEntity):
    def __init__(self, api = None):
        TgEntity.__init__(self, {
            "id":           ("id", None),
            "type":         ("type", None),
            "title":        ("title", None),
            "username":     ("username", None),
            "first_name":   ("first_name", None),
            "last_name":    ("last_name", None)
        })
        self.api = api

    def send_message(self, text = "", parse_mode = None, disable_web_page_review = False, disable_notification = False, reply_to_message = None, reply_markup = None):
        if self.id == None or self.api == None: raise Exception("Can't send API requests with this chat instance")
        return self.api.send_message(
            chat_id = self.id,
            text = text,
            parse_mode = parse_mode,
            disable_web_page_review = disable_web_page_review,
            disable_notification = disable_notification,
            reply_to_message = reply_to_message,
            reply_markup = reply_markup.json() if reply_markup != None else None
        )

    @classmethod
    def build(cls, data, api = None):
        entity = cls(api)
        entity._set_props(data)
        return entity

class User(TgEntity):
    def __init__(self):
        TgEntity.__init__(self, {
            "id":           ("id", None),
            "first_name":   ("first_name", None),
            "last_name":    ("last_name", None),
            "username":     ("username", None)
        })

class Message(TgEntity):
    def __init__(self, api):
        TgEntity.__init__(self, {
            "id":                       ("message_id", None),
            "date":                     ("date", 0),
            "forward_date":             ("forward_date", None),
            "edit_date":                ("edit_date", None),
            "text":                     ("text", None),
            "caption":                  ("caption", None),
            "delete_chat_photo":        ("delete_chat_photo", False),
            "group_chat_created":       ("group_chat_created", False),
            "supergroup_chat_created":  ("supergroup_chat_created", False),
            "channel_chat_created":     ("channel_chat_created", False),
            "migrate_to_chat_id":       ("migrate_to_chat_id", None),
            "migrate_from_chat_id":     ("migrate_from_chat_id", None),
        })
        self.api = api

    def is_service_message(self):
        return self.delete_chat_photo or self.group_chat_created or self.supergroup_chat_created or self.channel_chat_created or self.migrate_to_chat_id != None or self.migrate_from_chat_id != None

    def _update_msg_cb(self, message):
        self.text = message.text
        self.caption = message.caption

    def forward(self, to_chat_id, disable_notification = False):
        if self.api == None or self.id == None:
            raise Exception("This message is not sent")
        return self.api.forward_message(
            chat_id = self.to_chat_id,
            from_chat_id = self.chat_id,
            disable_notification = disable_notification,
            message_id = self.id
        )

    def edit_text(self, text, parse_mode = None, reply_markup = None):
        if self.api == None or self.id == None:
            raise Exception("This message is not sent")
        return self.api.edit_message_text(
            chat_id = self.chat_id,
            message_id = self.id,
            text = text,
            parse_mode = parse_mode,
            reply_markup = reply_markup.json() if reply_markup != None else None
        ).then(self._update_msg_cb)

    def edit_caption(self, caption, reply_markup = None):
        if self.api == None or self.id == None:
            raise Exception("This message is not sent")
        return self.api.edit_message_caption(
            chat_id = self.chat_id,
            message_id = self.id,
            caption = caption,
            reply_markup = reply_markup.json() if reply_markup != None else None
        ).then(self._update_msg_cb)

    def edit_reply_markup(self, reply_markup):
        if self.api == None or self.id == None:
            raise Exception("This message is not sent")
        return self.api.edit_message_reply_markup(
            chat_id = self.chat_id,
            message_id = self.id,
            reply_markup = reply_markup.json()
        )

    def _set_props(self, values = {}):
        TgEntity._set_props(self, values)
        self.chat_id = values["chat"]["id"] if "chat" in values else None
        self.user_id = values["from"]["id"] if "from" in values else None

        self.forward_from = User.build(values["forward_from"]) if "forward_from" in values else None
        self.forward_from_chat = Chat.buid(values["forward_from_chat"]) if "forward_from_chat" in values else None
        self.reply_to_message = Message.build(values["reply_to_message"]) if "reply_to_message" in values else None
        #TODO other entities

    @classmethod
    def build(cls, data, api = None):
        entity = cls(api)
        entity._set_props(data)
        return entity
