import threading
import sqlite3

from tgbot import Bot, dialogue

class UserWithPersistentData(dialogue.User):
    def __init__(self):
        dialogue.User.__init__(self)
        self.data = {}

class ChatWithPersistentData(dialogue.Chat):
    def __init__(self, api):
        dialogue.Chat.__init__(self, api)
        self.data = {}

class PersistentBot(Bot):
    def __init__(self, database_path, *args, **kwargs):
        Bot.__init__(self, user_cls = UserWithPersistentData, chat_cls = ChatWithPersistentData, *args, **kwargs)
        self.mutex = threading.Lock()
        self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()
        self.create_tables_ifnexists()

    def create_tables_ifnexists(self):
        self.cursor.execute("create table if not exists users (id text unique, first_name text, last_name text, username text, data text)")
        self.cursor.execute("create table if not exists chats (id text unique, type text, title text, username text, first_name text, last_name text, data text)")

    def save(self):
        self.mutex.acquire()
        for chat in self.chats:
            pass
        for user in self.users:
            pass
        self.mutex.release()

    def stop(self):
        self.save()
        self.mutex.acquire()
        self.cursor.close()
        self.connection.close()
        self.mutex.release()
        Bot.stop(self)
