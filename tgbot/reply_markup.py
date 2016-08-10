import json

class ReplyMarkup(object):
    def dict(self):
        raise NotImplementedError()

    def json(self):
        return json.dumps(self.dict())

    def __str__(self):
        return str(self.dict())

class ReplyKeyboardMarkup(ReplyMarkup):
    def __init__(self, buttons = [], resize_keyboard = False, one_time_keyboard = False, selective = False):
        self.buttons = buttons
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective

    def dict(self):
        return {
            "keyboard": [[button.dict() for button in row] for row in self.buttons],
            "resize_keyboard": self.resize_keyboard,
            "one_time_keyboard": self.one_time_keyboard,
            "selective": self.selective
        }

class KeyboardButton(object):
    def __init__(self, text = "", request_contact = False, request_location = False):
        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location

    def dict(self):
        return {
            "text": self.text,
            "request_contact": self.request_contact,
            "request_location": self.request_location
        }

class ReplyKeyboardHide(ReplyMarkup):
    def __init__(self, selective = False):
        self.selective = selective

    def dict(self):
        return {
            "hide_keyboard": True,
            "selective": self.selective
        }

class InlineKeyboardMarkup(ReplyMarkup):
    def __init__(self, buttons = []):
        self.buttons = buttons

    def dict(self):
        return {
            "inline_keyboard": [[button.dict() for button in row] for row in self.buttons]
        }

class InlineKeyboardButton(object):
    def __init__(self, text = "", url = None, callback_data = None, switch_inline_query = None):
        self.text = text
        self.url = url
        self.callback_data = callback_data
        self.switch_inline_query = switch_inline_query

    def dict(self):
        obj = {
            "text": self.text
        }
        if self.url == None and self.callback_data == None and self.switch_inline_query == None:
            raise Exception("At least one of url, callback_data or switch_inline_query should be set")
        if self.url != None: obj["url"] = self.url
        if self.callback_data != None: obj["callback_data"] = self.callback_data
        if self.switch_inline_query != None: obj["switch_inline_query"] = self.switch_inline_query
        return obj

class ForceReply(ReplyMarkup):
    def __init__(self, selective = False):
        self.selective = selective

    def dict(self):
        return {
            "force_reply": True,
            "selective": self.selective
        }
