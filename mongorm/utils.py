import sys

def setdefaultattr(obj, name, default):
    if not hasattr(obj, name):
        setattr(obj, name, default)
    return getattr(obj, name)


def is_field(value, field_type=None, required=None):
    from .fields import BaseField
    if field_type:
        if isinstance(value, field_type):
            if required is None:
                return True
            elif required == value.required:
                return True
    elif type(value) in BaseField.__subclasses__():
        if required is None:
            return True
        elif required == value.required:
            return True


def is_embedded_doc(value):
    from .documents import EmbeddedDocument
    if type(value) in EmbeddedDocument.__subclasses__():
        return True


def dereference(dbref):
    from .connection import get_database
    db = get_database()
    doc = db.dereference(dbref)
    cls = getattr(sys.modules[__name__], dbref.collection)
    if dbref.id in cls.__memo__:
        document = cls.get_memo(doc["_id"])
        document.update_from(**doc)
    else:
        document = cls(**doc)
    return document
