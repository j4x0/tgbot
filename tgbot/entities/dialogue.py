from tgbot.entities import *
from tgbot.entities.files import *
from tgbot.entities.location import *

class Chat(RequestingEntity):
    def __init__(self, api):
        RequestingEntity.__init__(self, {
            "id":           ("id", None),
            "type":         ("type", None),
            "title":        ("title", None),
            "username":     ("username", None),
            "first_name":   ("first_name", None),
            "last_name":    ("last_name", None)
        }, api)

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

    def send_photo(self, photo, caption = None, disable_notification = False, reply_markup = None):
        if self.id == None or self.api == None: raise Exception("Can't send API requests with this chat instance")
        return self.api.send_photo(
            chat_id = self.id,
            photo = photo,
            caption = caption,
            disable_notification = disable_notification,
            reply_markup = reply_markup.json() if reply_markup != None else None
        )

    def send_audio(self, audio, duration = None, performer = None, title = None, disable_notification = False, reply_markup = None):
        if self.id == None or self.api == None: raise Exception("Can't send API requests with this chat instance")
        return self.api.send_audio(
            chat_id = self.id,
            audio = audio,
            duration = duration,
            performer = performer,
            title = title,
            disable_notification = disable_notification,
            reply_markup = reply_markup.json() if reply_markup != None else None
        )

    def send_document(self, document, caption = None, disable_notification = False, reply_markup = None):
        if self.id == None or self.api == None: raise Exception("Can't send API requests with this chat instance")
        return self.api.send_document(
            chat_id = self.id,
            document = document,
            caption = caption,
            disable_notification = disable_notification,
            reply_markup = reply_markup.json() if reply_markup != None else None
        )

    def send_sticker(self, sticker, disable_notification = False, reply_markup = None):
        if self.id == None or self.api == None: raise Exception("Can't send API requests with this chat instance")
        return self.api.send_sticker(
            chat_id = self.id,
            sticker = sticker,
            disable_notification = disable_notification,
            reply_markup = reply_markup.json() if reply_markup != None else None
        )

    def send_video(self, video, duration = None, width = None, height = None, caption = None, disable_notification = False, reply_markup = None):
        if self.id == None or self.api == None: raise Exception("Can't send API requests with this chat instance")
        return self.api.send_video(
            chat_id = self.id,
            video = video,
            duration = duration,
            width = width,
            height = height,
            caption = caption,
            disable_notification = disable_notification,
            reply_markup = reply_markup.json() if reply_markup != None else None
        )

    def send_voice(self, voice, duration = None, disable_notification = False, reply_markup = None):
        if self.id == None or self.api == None: raise Exception("Can't send API requests with this chat instance")
        return self.api.send_voice(
            chat_id = self.id,
            voice = voice,
            duration = duration,
            disable_notification = disable_notification,
            reply_markup = reply_markup.json() if reply_markup != None else None
        )

class User(Entity):
    def __init__(self):
        Entity.__init__(self, {
            "id":           ("id", None),
            "first_name":   ("first_name", None),
            "last_name":    ("last_name", None),
            "username":     ("username", None)
        })

class MessageEntity(Entity):
    def __init__(self):
        Entity.__init__(self, {
            "type":     ("type", None),
            "offset":   ("offset", None),
            "length":   ("length", None),
            "url":      ("url", None),
        })

    def _set_props(self, values = {}):
        Entity._set_props(self, values)
        self.user = User.build(values["user"]) if "user" in values else None

class Message(RequestingEntity):
    def __init__(self, api):
        RequestingEntity.__init__(self, {
            "id":                       ("message_id", None),
            "date":                     ("date", 0),
            "forward_date":             ("forward_date", None),
            "edit_date":                ("edit_date", None),
            "text":                     ("text", None),
            "caption":                  ("caption", None),
            "new_chat_title":           ("new_chat_title", None),
            "delete_chat_photo":        ("delete_chat_photo", False),
            "group_chat_created":       ("group_chat_created", False),
            "supergroup_chat_created":  ("supergroup_chat_created", False),
            "channel_chat_created":     ("channel_chat_created", False),
            "migrate_to_chat_id":       ("migrate_to_chat_id", None),
            "migrate_from_chat_id":     ("migrate_from_chat_id", None),
        }, api)

    def _update_msg_cb(self, message):
        self.text = message.text
        self.caption = message.caption

    def forward(self, to_chat_id, disable_notification = False):
        if self.api == None or self.id == None:
            raise Exception("This message is not sent")
        return self.api.forward_message(
            chat_id = to_chat_id,
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

    def is_service_message(self):
        return False #TODO

    def is_forwarded(self):
        return self.forward_from_chat != None

    def is_reply(self):
        return self.reply_to_message != None

    def is_photo(self):
        return len(self.photo) > 0

    def is_audio(self):
        return self.audio != None

    def is_document(self):
        return self.document != None

    def is_sticker(self):
        return self.sticker != None

    def is_video(self):
        return self.video != None

    def is_voice(self):
        return self.voice != None

    def is_location(self):
        return self.location != None

    def is_venue(self):
        return self.venue != None

    def _set_props(self, values = {}):
        RequestingEntity._set_props(self, values)
        self.chat_id = values["chat"]["id"] if "chat" in values else None
        self.user_id = values["from"]["id"] if "from" in values else None

        self.forward_from = User.build(values["forward_from"]) if "forward_from" in values else None
        self.forward_from_chat = Chat.buid(values["forward_from_chat"]) if "forward_from_chat" in values else None
        self.reply_to_message = Message.build(values["reply_to_message"], self.api) if "reply_to_message" in values else None
        self.entities = [MessageEntity.build(me_data) for me_data in values["entities"]] if "entities" in values else []

        self.audio = Audio.build(values["audio"], self.api) if "audio" in values else None
        self.document = Document.build(values["document"], self.api) if "document" in values else None
        self.photo = [PhotoSize.build(photosize_data, self.api) for photosize_data in values["photo"]] if "photo" in values else []
        self.sticker = Sticker.build(values["sticker"], self.api) if "sticker" in values else None
        self.video = Video.build(values["video"], self.api) if "video" in values else None
        self.voice = Voice.build(values["voice"], self.api) if "voice" in values else None

        self.location = Location.build(values["location"]) if "location" in values else None
        self.venue = Venue.build(values["venue"]) if "venue" in values else None
