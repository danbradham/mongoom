import sys
import weakref
from bson import DBRef
from copy import copy
from functools import partial
from .connection import get_database
from .utils import is_field
from .fields import Field, ObjectIdField, ValidationError


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


def cache_ref_deleted(cls, wref):
    found = None
    for _id, ref in cls.__cache__.iteritems():
        if ref == wref:
            found = _id
            break
    cls.__cache__.pop(found)


class MetaDocument(type):

    def __new__(cls, clsname, bases, attrs):

        attrs["_type"] = Field(str, default=clsname)
        attrs["_id"] = ObjectIdField()
        attrs["__cache__"] = {}
        for name, value in attrs.iteritems():
            if is_field(value):
                value.__dict__["name"] = name

        return super(MetaDocument, cls).__new__(cls, clsname, bases, attrs)


class Document(object):
    '''Incredibly bare. Embedded Documents are dictionaries with a key, "type",
    set to __class__.__name__. This allows for a simple decoding strategy:
    On document instantiation, if an attribute is a dictionary and has a type
    key, we replace the attribute with an instance of type'''

    __metaclass__ = MetaDocument

    def __init__(self, *args, **kwargs):
        if "_id" in kwargs and not kwargs["_id"] in self.__cache__:
            self.cache(kwargs["_id"])
        self._data = {}
        for name, value in kwargs.iteritems():
            setattr(self, name, value)
        for name, field in self.fields.iteritems():
            if field.default is not None:
                defl = (copy(field.default) if not callable(field.default)
                        else field.default())
                self._data.setdefault(name, defl)

    @property
    def ref(self):
        if not "_id" in self.data:
            self.save()
        return DBRef(self._type, self._id)

    @property
    def fields(self):
        return dict((k, v) for k, v in self.__class__.__dict__.iteritems()
                    if is_field(v))

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def cache(self, _id):
        self.__cache__[_id] = weakref.ref(
            self, partial(cache_ref_deleted, self.__class__))

    @classmethod
    def get_cache(cls, _id):
        ref = cls.__cache__.get(_id)
        if ref:
            return ref()

    def validate(self):
        '''Ensure all required fields are in data.'''
        missing_fields = []
        for name, field in self.fields:
            if field.required and not field.name in self.data:
                missing_fields.append(field.name)

        if missing_fields:
            raise ValidationError(
                "{} missing fields: {}".format(self.name, missing_fields))

    def save(self, *args, **kwargs):
        '''Write _data dict to database.'''
        db = get_database()
        self.validate()
        if not "_id" in self.data:  # No id...insert document
            self._id = db[self._type].insert(self.data, *args, **kwargs)
            self.cache(self._id)
            return self
        db[self._type].update({"_id": self._id}, self.data, *args, **kwargs)
        return self

    @classmethod
    def generate_objects(cls, cursor):
        '''Generator that returns all documents from a pymongo cursor as their
        equivalent python class'''
        for doc in cursor:
            if doc["_id"] in cls.__cache__:
                document = cls.get_cache(doc["_id"])
                document.data = doc
            else:
                document = cls(**doc)
            yield document

    @classmethod
    def find(cls, decode=True, **spec):
        '''Find objects in a classes collection.'''
        db = get_database()
        docs = db[cls._type].find(spec)
        if not decode:
            return docs
        return cls.generate_objects(docs)

    @classmethod
    def find_one(cls, decode=True, **spec):
        db = get_database()
        doc = db[cls._type].find_one(spec)
        if not decode:
            return doc

        if doc["_id"] in cls.__cache__:
            document = cls.get_cache(doc["_id"])
            document.data = doc
        else:
            document = cls(**doc)
        return document

    def remove(self, *args, **kwargs):
        db = get_database()
        if "_id" in self.data:
            db[self._type].remove({"_id": self._id})
