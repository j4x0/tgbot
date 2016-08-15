from tgbot import Bot, dialogue, logging

class PersistentUser(dialogue.User):
    def __init__(self):
        dialogue.User.__init__(self)
        self.data = {}

class PersistentChat(dialogue.Chat):
    def __init__(self, api):
        dialogue.Chat.__init__(self, api)
        self.data = {}

class Storage(object):
    def save_user(self, user):
        raise NotImplementedError()

    def save_users(self, bot):
        raise NotImplementedError()

    def save_chats(self, bot):
        raise NotImplementedError()

    def load_users(self, bot):
        raise NotImplementedError()

    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

class PersistentBot(Bot):
    def __init__(self, storage, *args, **overwrite_kwargs):
        kwargs = {"user_cls": PersistentUser, "chat_cls": PersistentChat}
        kwargs.update(overwrite_kwargs)
        Bot.__init__(self, *args, **kwargs)
        self.storage = storage

    def save(self):
        logging.info("Saving users and chats")
        self.storage.save_chats(self)
        self.storage.save_users(self)

    def load(self):
        logging.info("Loading users and chats")
        self.storage.load_chats(self)
        self.storage.load_users(self)

    def start(self):
        logging.log("Opening storage")
        self.storage.open()
        self.load()
        Bot.start(self)

    def stop(self):
        try:
            self.save()
        except Exception as e:
            logging.error(str(e))
        logging.log("Closing storage")
        self.storage.close()
        Bot.stop(self)
