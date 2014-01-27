from .utils import setdefaultattr


def embedded_docs():
    from .doc import EmbeddedDocument
    return EmbeddedDocument.__subclasses__()


class ValidationError(Exception):
    pass


class BaseField(object):
    """Defines a basic interface for all fields. Fields are used as class
    attributes on Document objects to define their schema. Fields validate
    themselves when a Document object calls it's validate method(typically
    on save)."""

    def __init__(self, _type, default=None, required=False):
        self._type = _type
        self.default = default
        self.required = required

    def validate(self, obj, name):
        '''Returns a tuple (value(int), msg(str))
        Acceptable return values:
        -1 : obj.name validates
        0  : obj.name is missing
        1  : obj.name is the wrong type'''
        pass


class Field(BaseField):
    '''Validates an attribute.'''

    def validate(self, obj, name):
        msg = None
        if self.default:
            setdefaultattr(obj, name, self.default)

        exists = hasattr(obj, name)
        if self.required and not exists:
            return -1, msg

        if exists:
            if not isinstance(getattr(obj, name), self._type):
                return 0, msg
            elif type(getattr(obj, name)) in embedded_docs():
                obj.validate()

        return 1, msg


class ListField(BaseField):
    '''Validates that attribute is a list and that each child is of
    a certain type.'''

    def validate(self, obj, name):
        msg = None
        exists = hasattr(obj, name)
        if self.required and not exists:
            return -1, msg
        if exists and not isinstance(getattr(obj, name), list):
            return 0, msg
        elif exists:
            for list_item in getattr(obj, name):
                if not isinstance(list_item, self._type):
                    msg = "includes: {} {}"
                    return 0, msg.format(list_item, type(list_item))
                if type(list_item) in embedded_docs():
                    list_item.validate()

        return 1, msg
