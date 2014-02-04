

def setdefaultattr(obj, name, default):
    if not hasattr(obj, name):
        setattr(obj, name, default)
    return getattr(obj, name)


def rget_subclasses(cls):
    subclasses = cls.__subclasses__()
    for subcls in subclasses:
        subclasses.extend(rget_subclasses(subcls))
    return subclasses


def is_field(value, field_type=None, required=None):
    from .fields import BaseField
    if field_type:
        if isinstance(value, field_type):
            if required is None:
                return True
            elif required == value.required:
                return True
    elif type(value) in rget_subclasses(BaseField):
        if required is None:
            return True
        elif required == value.required:
            return True


def is_embedded_doc(value):
    from .documents import EmbeddedDocument
    if type(value) in EmbeddedDocument.__subclasses__():
        return True
