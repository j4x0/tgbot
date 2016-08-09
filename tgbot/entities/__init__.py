class Entity(object):
    def __init__(self, props):
        self._props = props
        self._set_props()

    def _set_props(self, values = {}):
        for prop_name, (field_name, default_value) in self._props.iteritems():
            value = values[field_name] if field_name in values else default_value
            setattr(self, prop_name, value)

    def update_properties(self, values):
        self._set_props(values)

    @classmethod
    def build(cls, data):
        entity = cls()
        entity._set_props(data)
        return entity

class RequestingEntity(Entity):
    def __init__(self, props, api):
        Entity.__init__(self, props)
        self.api = api

    @classmethod
    def build(cls, data, api = None):
        entity = cls(api)
        entity._set_props(data)
        return entity
