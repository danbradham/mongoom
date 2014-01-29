import sys


def encode(v):
    pass


def decode(v):
    if isinstance(v, dict):
        if "_type" in v:
            v_cls = getattr(sys.modules[__name__], v["_type"])
            obj = decode(v_cls(v))
            for k, v in obj.iteritems():
                obj[k] = decode(v)
        return obj
    if isinstance(v, list):
        l = []
        for item in v:
            l.append(decode(v))
        return l
    return v


class MetaDocument(type):

    def __new__(cls, clsname, bases, attrs):

        for name, value in attrs.iteritems():
            if is_field(value):
                value.name = name
        attrs["_type"] = clsname

        return super(MetaDocument, cls).__new__(cls, clsname, bases, attrs)


class EmbeddedDocument(dict):
    '''Incredibly bare. Embedded Documents are dictionaries with a key, "type",
    set to __class__.__name__. This allows for a simple decoding strategy:
    On document instantiation, if an attribute is a dictionary and has a type
    key, we replace the attribute with an instance of type'''

    __metaclass__ = MetaDocument

    def __init__(self, *args, **kwargs):
        super(EmbeddedDocument, self).__init__(*args, **kwargs)
        self._type = self.__class__.__name__
