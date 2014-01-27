import sys
from bson import DBRef
from .fields import BaseField, ListField, Field, ValidationError
from .utils import setdefaultattr
from .connect import get_connection


def is_embedded(document):
    if type(document) in EmbeddedDocument.__subclasses__():
        return True


def encode(document):
    '''Recursively replace python objects with dictionary representations
    allowing them to be serialized with bson/json.

    :param document: An object that inherits from BaseDoc
    Returns a flattened dictionary.
    '''

    doc = document.__dict__()
    encoded = {}
    for field, value in doc.iteritems():
        if is_embedded(value):
            encoded[field] = encode(value)
            continue
        if isinstance(value, list):
            encoded[field] = []
            for item in value:
                if is_embedded(item):
                    encoded[field].append(encode(item))
                    continue
                encoded[field].append(item)
            continue
        encoded[field] = value

    return encoded


def conv_doc(doc):
    doc_cls = getattr(sys.modules[__name__], doc["type"])
    decoded = decode(doc_cls(**doc))
    return decoded


def decode(document):
    for field, value in document.__dict__.iteritems():
        if isinstance(value, dict):
            if "type" in value:
                document.field = conv_doc(value)
                continue
        if isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    if "type" in value:
                        document.field[i] = conv_doc(document, item)
                        continue
    return document


class MetaDoc(type):

    def __new__(cls, clsname, bases, attrs):

        cls_attrs = {"fields": {}}
        for name, value in attrs.iteritems():
            if type(value) in BaseField.__subclasses__():
                cls_attrs["fields"][name] = value
            else:
                cls_attrs[name] = value

        def objects(cls):
            docs = cls.db[cls.type].find()
            for doc in docs:
                yield cls(**doc)

        cls_attrs["objects"] = property(objects)

        return super(MetaDoc, cls).__new__(cls, clsname, bases, cls_attrs)

    def __init__(self, name, bases, attrs):
        super(MetaDoc, self).__init__(name, bases, attrs)
        self.type = name


class BaseDocument(object):
    __metaclass__ = MetaDoc

    def __init__(self, **fields):
        self.__dict__.update(fields)
        self.db = get_connection()

    def remove(self):
        self.db["_type"].remove()

    def save(self, validate=True, *args, **kwargs):
        if validate:
            self.validate()
        print self.__dict__
        encoded = encode(self.__dict__)
        print encoded
        if not hasattr(self, "_id"):
            # _id = self.db[self.type].insert(encoded)
            # self._id = _id
            return

        #self.db[self.type].update({"_id": self._id}, encoded)

    def validate(self):
        '''Calls the validate method for each field in the classes schema.'''
        missing_fields = []
        incorrect_types = []
        for name, field in self.fields.iteritems():
            valid, msg = field.validate(self, name)
            if valid == -1:
                missing_fields.append(name)
            if valid == 0:
                if msg:
                    incorrect_types.append((name, msg))
                else:
                    incorrect_types.append(
                        (name, type(getattr(self, name)), field.type))

        errors = []
        if missing_fields:
            errors.append("Missing required fields: {}".format(missing_fields))
        if incorrect_types:
            errors.append("Incorrect types: {}".format(incorrect_types))
        if errors:
            raise ValidationError("\n".join(errors))

        return True

    @classmethod
    def get(cls, **spec):
        doc = cls.db[cls.type].find_one(spec)
        decoded = decode(cls(**doc))
        return decoded


class Document(BaseDocument):

    children = ListField(DBRef)
    parent = Field(DBRef)

    def __iadd__(self, document):
        setdefaultattr(self, "children", []).append(document.ref)
        setdefaultattr(document, "parent", self.ref)

    def __isub__(self, document):
        self.children.remove(document.ref)
        document.parent = None
        document.remove()

    def remove(self, refs=True):
        if refs:
            for child in self.children:
                self -= child
        super(Document, self).remove()

    @property
    def ref(self):
        return DBRef(self.type, self._id)

    @property
    def components(self):
        for child in self.children:
            doc = self.db.dereference(child)
            decoded = decode(getattr(sys.modules[__name__], doc["type"]), doc)
            yield decoded

    @property
    def parent(self):
        doc = self.db.dereference(self.parent)
        decoded = decode(getattr(sys.modules[__name__], doc["type"]), doc)
        return decoded


class EmbeddedDocument(BaseDocument):

    _parent = None

    def __init__(self, parent, **fields):
        self.update(fields)
        self._parent = parent

    @property
    def parent(self):
        return self._parent
