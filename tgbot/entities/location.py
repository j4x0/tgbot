from tgbot.entities import Entity

class Location(Entity):
    def __init__(self):
        Entity.__init__(self, {
            "longitude":    ("longitude", None),
            "latitude":     ("latitude", None)
        })


class Venue(Entity):
    def __init__(self):
        Entity.__init__(self, {
            "title":            ("title", None),
            "address":          ("address", None),
            "foursquare_id":    ("foursquare_id", None)
        })

    def _set_props(self, values = {}):
        Entity._set_props(self, values)
        self.location = Location.build(values["location"]) if "location" in values else None
