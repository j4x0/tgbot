import threading
import sqlite3
import json


from tgbot.ext.persistent import Storage, PersistentChat, PersistentUser

class ThreadsafeCursor(object):
    def __init__(self, connection):
        self._mutex = threading.Lock()
        self._connection = connection
        self._cursor = connection.cursor()

    def _inside(self):
        if self._mutex.acquire(False):
            self._mutex.release()
            return False
        else:
            return True

    def __enter__(self):
        self._mutex.acquire()

    def __exit__(self, type, value, traceback):
        self._connection.commit()
        self._mutex.release()

    def __getattr__(self, key):
        attr = getattr(self._cursor, key)
        if hasattr(attr, "__call__"):
            def wrap(*args, **kwargs):
                if not self._inside():
                    raise RuntimeError("Can only call cursor functions inside with block")
                return attr(*args, **kwargs)
            return wrap
        else:
            return attr

class SQLiteStorage(Storage):
    def __init__(self, database_path):
        self.database_path = database_path
        self.connection = None
        self.cursor = None

    def create_tables_ifnexists(self):
        with self.cursor:
            self.cursor.execute("create table if not exists chats (id text unique, type text, title text, username text, first_name text, last_name text, data text)")
            self.cursor.execute("create table if not exists users (id text unique, first_name text, last_name text, username text, data text)")

    def load_chats(self, bot):
        with self.cursor:
            for (id, type, title, username, first_name, last_name, data_json) in self.cursor.execute("select * from chats"):
                try: id = int(id) # Try to convert back to int (will fail for channels)
                except: pass
                bot.add_chat(id, {
                    "type": type, "username": username, "first_name": first_name, "last_name": last_name # Data as sent by Telegram API
                })
                try:
                    bot.chats[id].data = json.loads(data_json)
                except: pass

    def load_users(self, bot):
        with self.cursor:
            for (id, first_name, last_name, username, data_json) in self.cursor.execute("select * from users"):
                try: id = int(id) # Try to convert back to int (will fail for channels)
                except: pass
                bot.add_user(id, {
                    "first_name": first_name, "last_name": last_name, "username": username # Data as sent by Telegram API
                })
                try:
                    bot.users[id].data = json.loads(data_json)
                except: pass

    def sql_value(self, var):
        return str(var) if var is not None else "NULL"

    def save_chats(self, bot):
        with self.cursor:
            for chat in bot.chats.values():
                self.cursor.execute("insert or ignore into chats(id) values (?)", [self.sql_value(chat.id)])
                self.cursor.execute(
                    "update chats set type = ?, title = ?, username = ?, first_name = ?, last_name = ?, data = ? WHERE id = ?",
                    [self.sql_value(x) for x in [chat.type, chat.title, chat.username, chat.first_name, chat.last_name, json.dumps(chat.data), chat.id]])

    def save_users(self, bot):
        with self.cursor:
            for user in bot.users.values():
                self.cursor.execute("insert or ignore into users(id) values (?)", [self.sql_value(user.id)])
                self.cursor.execute(
                    "update users set first_name = ?, last_name = ?, username = ?, data = ? WHERE id = ?",
                    [self.sql_value(x) for x in [user.first_name, user.last_name, user.username, json.dumps(user.data), user.id]])

    def open(self):
        self.connection = sqlite3.connect(self.database_path)
        self.cursor = ThreadsafeCursor(self.connection)
        self.create_tables_ifnexists()

    def close(self):
        with self.cursor:
            self.cursor.close()
        self.connection.close()
