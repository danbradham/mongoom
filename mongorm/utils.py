

def setdefaultattr(obj, name, default):
    if not hasattr(obj, name):
        setattr(obj, name, default)
    return getattr(obj, name)


def is_field(value, field_type=None):
    from .fields import BaseField
    if field_type:
        if isinstance(value, field_type):
            return True
    elif type(value) in BaseField.__subclasses__():
        return True


def is_embedded_doc(value):
    from .doc import EmbeddedDocument
    if type(value) in EmbeddedDocument.__subclasses__():
        return True
