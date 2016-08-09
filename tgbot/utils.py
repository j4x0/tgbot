class Enum(object):
    def __init__(self, items):
        self.items = items

    def __getattr__(self, key):
        return self.items[key]

    def __setattr__(self, key, value):
        raise AttributeError("Cannot set enum attributes")

def create_enum(items):
    return Enum(items)
