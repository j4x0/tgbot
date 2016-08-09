from tgbot.entities import RequestingEntity

class FileEntity(RequestingEntity):
    def __init__(self, props, api):
        props.update({
            "id":           ("file_id", None),
            "size":         ("file_size", None),
            "mime_type":    ("mime_type", None)
        })
        RequestingEntity.__init__(self, props, api)

    def download(self, name):
        if self.api == None or self.id == None:
            raise Exception("Can't make requests with this file")
        return self.api.download_file(self.id, name)

class PhotoSize(FileEntity):
    def __init__(self, api):
        FileEntity.__init__(self, {
            "width":    ("width", None),
            "height":   ("height", None)
        }, api)

class FileEntityWithThumb(FileEntity):
    def _set_props(self, values = {}):
        FileEntity._set_props(self, values)
        self.thumb = PhotoSize.build(values["thumb"], self.api) if "thumb" in values else None



class Audio(FileEntity):
    def __init__(self, api):
        FileEntity.__init__(self, {
            "duration":     ("duration", None),
            "performer":    ("performer", None),
            "title":        ("title", None)
        }, api)

class Document(FileEntityWithThumb):
    def __init__(self, api):
        FileEntityWithThumb.__init__(self, {
            "name": ("file_name", None)
        }, api)

class Sticker(FileEntityWithThumb):
    def __init__(self, api):
        FileEntityWithThumb.__init__(self, {
            "width":    ("width", None),
            "height":   ("height", None),
            "emoji":    ("emoji", None)
        }, api)

class Video(FileEntityWithThumb):
    def __init__(self, api):
        FileEntityWithThumb.__init__(self, {
            "width":    ("width", None),
            "height":   ("height", None),
            "duration": ("duration", None)
        })

class Voice(FileEntity):
    def __init__(self, api):
        FileEntity.__init__(self, {
            "duration": ("duration", None)
        })
