class APIEntity(object):
    def populate(self, data, keys):
        for key in data:
            if key not in keys: pass
            setattr(self, key, data[key])

    @staticmethod
    def deserialize(data):
        raise NotImplementedError()

class Update(APIEntity):
    def __init__(self, id):
        self.id = id
        self.message = None
        self.edited_message = None
        self.inline_query = None
        self.chosen_inline_result = None
        self.callback_query = None

    @staticmethod
    def deserialize(data):
        update = Update(data["update_id"])
        update.message = Message.deserialize(data["message"]) if "message" in data else None
        return update

class Message(APIEntity):
    def __init__(self, id, date, chat):
        self.id = id
        self.date = date
        self.chat = chat

        self.user = None

        self.forwarded_from = None
        self.forward_from_chat = None
        self.forward_date = None

        self.reply_to_message = None
        self.edit_date = None
        self.text = None
        self.entities = []

        self.audio = None
        self.document = None
        self.sticker = None
        self.video = None
        self.voice = None
        self.caption = None
        self.contact = None
        self.venue = None

        self.new_chat_member = None
        self.left_chat_member = None
        self.new_chat_title = None
        self.new_chat_photo = None
        self.delete_chat_photo = False

        self.group_chat_created = False
        self.supergroup_chat_created = False

        self.migrate_to_chat_id = None
        self.migrate_from_chat_id = None

        self.pinned_message = None

    @staticmethod
    def deserialize(data):
        message = Message(data["message_id"], data["date"], None)
        message.populate(data, ["text", "edit_date", "caption", "new_chat_title", "delete_chat_photo", "group_chat_created", "supergroup_chat_created", "migrate_to_chat_id", "migrate_from_chat_id"])
        return message
