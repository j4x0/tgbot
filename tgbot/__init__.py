import telegram
import multiprocessing
import threading
import Queue
import math

from async.workers import WorkerPool
from entities import dialogue, callback
from telegram import *
from receivers import WebhookReceiver, APIReceiver
import events
import logging


class Bot(object):
    def __init__(
        self, token,
        limited_api = True, requests_per_second = 10, messages_to_chat_per_second = 1,
        use_webhook = False, webhook_port = 8443, openssl_command = "openssl",
        chat_cls = dialogue.Chat, user_cls = dialogue.User):

        self.token = token
        self._limited_api = limited_api

        # Initialize 40 worker threads
        self.events_worker_pool = WorkerPool(20)
        self.api_worker_pool = WorkerPool(20)

        if self._limited_api:
            self.api = AsyncifiedAPI(LimitedBotAPI(self.token, requests_per_second, messages_to_chat_per_second), self.api_worker_pool)
        else:
            self.api = AsyncifiedAPI(BotAPI(self.token), self.api_worker_pool)

        self.updates = multiprocessing.Queue()

        if use_webhook:
            self.receiver = WebhookReceiver(token, self.updates, port = webhook_port, openssl_command = openssl_command)
        else:
            self.receiver = APIReceiver(token, self.updates)

        self.chat_cls = chat_cls
        self.user_cls = user_cls
        self.chats = {}
        self.users = {}

        self.init_events()

    def init_events(self):
        self.on_message = events.MessageEvent(self.events_worker_pool)
        self.on_audio = events.AsyncEvent(self.events_worker_pool)
        self.on_document = events.AsyncEvent(self.events_worker_pool)
        self.on_photo = events.AsyncEvent(self.events_worker_pool)
        self.on_sticker = events.AsyncEvent(self.events_worker_pool)
        self.on_video = events.AsyncEvent(self.events_worker_pool)
        self.on_voice = events.AsyncEvent(self.events_worker_pool)
        self.on_location = events.AsyncEvent(self.events_worker_pool)
        self.on_venue = events.AsyncEvent(self.events_worker_pool)

        self.on_callback_query = events.CallbackQueryEvent(self.events_worker_pool)

    def _get_and_update_chat(self, data):
        chat_data = data["chat"]
        chat_id = chat_data["id"]
        if chat_id in self.chats:
            self.chats[chat_id].update_properties(chat_data)
        else:
            self.add_chat(chat_id, chat_data)
        return self.chats[chat_id]

    def _get_and_update_user(self, data):
        if "from" not in data:
            return None
        user_data = data["from"]
        user_id = user_data["id"]
        if user_id in self.users:
            self.users[user_id].update_properties(user_data)
        else:
            self.add_user(user_id, user_data)
        return self.users[user_id]

    def add_chat(self, chat_id, chat_data = {}):
        chat_data["id"] = chat_id
        self.chats[chat_id] = self.chat_cls.build(chat_data, self.api)

    def add_user(self, user_id, user_data = {}):
        user_data["id"] = user_id
        self.users[user_id] = self.user_cls.build(user_data)

    def process_message(self, chat, user, message):
        if message.is_audio():
            self.on_audio.emit(chat, user, message)
        elif message.is_document():
            self.on_document.emit(chat, user, message)
        elif message.is_photo():
            self.on_photo.emit(chat, user, message)
        elif message.is_sticker():
            self.on_sticker.emit(chat, user, message)
        elif message.is_video():
            self.on_video.emit(chat, user, message)
        elif message.is_voice():
            self.on_voice.emit(chat, user, message)
        elif message.is_service_message():
            pass #TODO
        elif message.is_location():
            self.on_location.emit(chat, user, message)
        elif message.is_venue():
            self.on_venue.emit(chat, user, message)
        else:
            self.on_message.emit(chat, user, message)

    def process_update(self, update):
        if "message" in update:
            message_data = update["message"]
            self.process_message(
                self._get_and_update_chat(message_data),
                self._get_and_update_user(message_data),
                dialogue.Message.build(message_data, self.api))
        if "callback_query" in update:
            callback_query_data = update["callback_query"]
            self.on_callback_query.emit(
                self._get_and_update_user(callback_query_data),
                callback.CallbackQuery.build(callback_query_data, self.api))

    def process_updates(self):
        while True:
            try:
                update = self.updates.get(True, 5)
            except Queue.Empty:
                continue
            if update == None: break # Receive process sent stop signa
            self.process_update(update)

    def start(self):
        logging.info("Bot is starting")

        self.receiver.setup()

        # Start threads and processes
        if self._limited_api:
            self.api.underlying_api().start()

        self.receiver.start()

        self.events_worker_pool.start()
        self.api_worker_pool.start()

        try:
            self.process_updates()
        except KeyboardInterrupt: pass
        finally:
            self.stop()

    def stop(self):
        logging.info("Bot is stopping")

        if self._limited_api:
            self.api.underlying_api().stop()

        self.receiver.terminate()
        self.receiver.join()

        self.events_worker_pool.stop()
        self.api_worker_pool.stop()
