import sys
import weakref
from bson import DBRef
from copy import copy
from functools import partial
from .connection import get_database
from .utils import is_field
from .fields import Field, ObjectIdField


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


def memo_ref_deleted(cls, wref):
    found = None
    for _id, ref in cls.__memo__.iteritems():
        if ref == wref:
            found = _id
            break
    cls.__memo__.pop(found)


class MetaDocument(type):

    def __new__(cls, clsname, bases, attrs):

        for name, value in attrs.iteritems():
            if is_field(value):
                value.__dict__["name"] = name
        attrs["_type"] = clsname
        attrs["__memo__"] = {}

        return super(MetaDocument, cls).__new__(cls, clsname, bases, attrs)


class Document(object):
    '''Incredibly bare. Embedded Documents are dictionaries with a key, "type",
    set to __class__.__name__. This allows for a simple decoding strategy:
    On document instantiation, if an attribute is a dictionary and has a type
    key, we replace the attribute with an instance of type'''

    __metaclass__ = MetaDocument
    _type = Field(str)
    _id = ObjectIdField()

    def __init__(self, *args, **kwargs):
        if "_id" in kwargs and not kwargs["_id"] in self.__memo__:
            self.memoize(kwargs["_id"])
        self._data = {"_type": self.__class__.__name__}
        for name, value in kwargs.iteritems():
            setattr(self, name, value)
        for field in self.fields:
            if field.default is not None:
                print field.default
                defl = (copy(field.default) if not callable(field.default)
                        else field.default())
                print defl
                self._data.setdefault(field.name, defl)

    @property
    def ref(self):
        if not "_id" in self._data:
            self.save()
        return DBRef(self._type, self._id)

    @property
    def fields(self):
        return [v for k, v in self.__class__.__dict__.iteritems()
                if is_field(v)]

    def save(self, *args, **kwargs):
        '''Write _data dict to database.'''
        db = get_database()
        if not "_id" in self._data:  # No id...insert document
            self._id = db[self._type].insert(self._data, *args, **kwargs)
            self.memoize(self._id)
            return self
        db[self._type].update({"_id": self._id}, self._data, *args, **kwargs)
        return self

    def update_from(self, **data):
        self._data.update(data)

    def memoize(self, _id):
        self.__memo__[_id] = weakref.ref(
            self, partial(memo_ref_deleted, self.__class__))

    @classmethod
    def get_memo(cls, _id):
        ref = cls.__memo__.get(_id)
        if ref:
            return ref()

    @classmethod
    def generate_objects(cls, cursor):
        '''Generator that returns all documents from a pymongo cursor as their
        equivalent python class'''
        for doc in cursor:
            if doc["_id"] in cls.__memo__:
                document = cls.get_memo(doc["_id"])
                document.update_from(**doc)
            else:
                document = cls(**doc)
            yield document

    @classmethod
    def find(cls, py_obj=True, **spec):
        '''Find objects in a classes collection.'''
        db = get_database()
        docs = db[cls._type].find(spec)
        if not py_obj:
            return docs
        return cls.generate_objects(docs)

    @classmethod
    def find_one(cls, py_obj=True, **spec):
        db = get_database()
        doc = db[cls._type].find_one(spec)
        if not py_obj:
            return doc

        if doc["_id"] in cls.__memo__:
            document = cls.get_memo(doc["_id"])
            document.update_from(**doc)
        else:
            document = cls(**doc)
        return document

    def remove(self):
        db = get_database()
        if "_id" in self._data:
            db[self._type].remove({"_id": self._id})
