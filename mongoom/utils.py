

def setdefaultattr(obj, name, default):
    if not hasattr(obj, name):
        setattr(obj, name, default)
    return getattr(obj, name)


def rget_subclasses(cls):
    subclasses = cls.__subclasses__()
    for subcls in subclasses:
        subclasses.extend(rget_subclasses(subcls))
    return subclasses


def is_field(value):
    from .fields import BaseField
    all_fields = tuple([BaseField] + rget_subclasses(BaseField))
    if isinstance(value, all_fields):
            return True


def is_document(value):
    from .documents import MetaDocument
    if isinstance(value, MetaDocument):
        return True


def is_embedded(value):
    from .documents import MetaEmbedded
    if isinstance(value, MetaEmbedded):
        return True
