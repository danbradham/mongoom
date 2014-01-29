from copy import copy
from bson.objectid import ObjectId
from bson import DBRef


class ValidationError(Exception):
    pass


class BaseField(object):
    '''Defines a basic interface for all fields. Fields are used as class
    attributes on Document objects to define their schema. Fields validate
    themselves when a Document object calls it's validate method(typically
    on save).'''

    def __init__(self, _type, name=None, default=None, required=False):
        self._type = _type
        self.default = default
        self.required = required
        self.name = name

    def __get__(self, inst, cls):
        defl = (copy(self.default) if not callable(self.default)
                else self.default())
        return inst._data.setdefault(self.name, defl)

    def __set__(self, inst, value):
        self.validate(value)
        inst._data.__setitem__(self.name, value)

    def validate(self, value):
        if isinstance(value, self._type):
            return True
        raise ValidationError("Value is not a {}".format(self._type))


class Field(BaseField):
    pass


class ObjectIdField(BaseField):

    def __init__(self, _type=ObjectId, default=None, required=False):
        super(ObjectIdField, self).__init__(_type, default, required)


class RefField(BaseField):

    def __init__(self, _type=DBRef, default=None, required=False):
        super(RefField, self).__init__(_type, default, required)

    def __set__(self, inst, value):
        try:
            self.validate(value)
        except ValidationError:
            value = value.ref
            self.validate(value)
        inst._data[self.name] = value


class ListField(BaseField):

    def validate(self, value):
        for item in value:
            if not isinstance(value, self._type):
                raise ValidationError(
                    "Value in ListField is not a {}".format(self._type))


class ListRefField(ListField):

    def __init__(self, _type=DBRef, default=None, required=False):
        super(ListRefField, self).__init__(_type, default, required)
