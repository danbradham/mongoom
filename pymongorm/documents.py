import weakref
from bson import DBRef
from copy import copy
from functools import partial
from .connection import get_collection, get_database
from .utils import is_field
from .fields import ObjectIdField, ValidationError, Field
from .utils import rget_subclasses


def cache_ref_deleted(cls, wref):
    found = None
    for _id, ref in cls.__cache__.iteritems():
        if ref == wref:
            found = _id
            break
    cls.__cache__.pop(found)


class MetaDocument(type):

    def __new__(cls, clsname, bases, attrs):
        attrs["_type"] = Field(basestring, default=clsname)
        attrs["_id"] = ObjectIdField()
        attrs["__cache__"] = {}
        for name, value in attrs.iteritems():
            if is_field(value):
                value.__dict__["name"] = name

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

        attrs["__init__"] = __init__

        return super(MetaDocument, cls).__new__(cls, clsname, bases, attrs)


class Document(object):
    '''Class attributes that are subclasses of BaseField are used to set the
    defaults of a Document's _data dictionary. The _data dictionary is the data
    entered into database. All _data is accessible through the data property of
    a Document, therefore it's imperative that you do not assign a Field to
    a class attribute named data for subclasses of Document.'''

    __metaclass__ = MetaDocument

    @property
    def ref(self):
        '''Returns a DBRef, saves before returning if _id not in data.'''
        if not "_id" in self.data:
            self.save()
        return DBRef(self._type, self._id)

    @property
    def fields(self):
        '''Returns all fields from baseclasses to allow for field
        inheritence. Collects fields top down ensuring that fields are properly
        overriden by subclasses.'''

        attrs = {}
        for obj in reversed(self.__class__.__mro__):
            attrs.update(obj.__dict__)
        return dict((k, v) for k, v in attrs.iteritems() if is_field(v))

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        for name, value in data.iteritems():
            setattr(self, name, value)

    def cache(self, _id):
        '''Document cache, used to ensure that only one object mapped to a db
        document is in memory at any given time.'''
        self.__cache__[_id] = weakref.ref(
            self, partial(cache_ref_deleted, self.__class__))

    @classmethod
    def get_cache(cls, _id):
        '''Returns a python object if the _id is cached in memory'''
        ref = cls.__cache__.get(_id)
        if ref:
            return ref()

    def validate(self):
        '''Ensure all required fields are in data.'''
        missing_fields = []
        for name, field in self.fields.iteritems():
            if field.required and not field.name in self.data:
                missing_fields.append(field.name)

        if missing_fields:
            raise ValidationError(
                "{} missing fields: {}".format(self.name, missing_fields))

    def save(self, *args, **kwargs):
        '''Write _data dict to database.'''
        col = get_collection(self.index(), self.collection())
        self.validate()
        if not "_id" in self.data:  # No id...insert document
            self._id = col.insert(self.data, *args, **kwargs)
            self.cache(self._id)
            return self
        col.update({"_id": self._id}, self.data, *args, **kwargs)
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
        col = get_collection(cls.index(), cls.collection())
        docs = col.find(spec)
        if not decode:
            return docs
        return cls.generate_objects(docs)

    @classmethod
    def find_one(cls, decode=True, **spec):
        col = get_collection(cls.index(), cls.collection())
        doc = col.find_one(spec)
        if not decode:
            return doc

        if doc["_id"] in cls.__cache__:
            document = cls.get_cache(doc["_id"])
            document.data = doc
        else:
            document = cls(**doc)
        return document

    def remove(self, *args, **kwargs):
        col = get_collection(self.index(), self.collection())
        if "_id" in self.data:
            col.remove({"_id": self._id})

    @classmethod
    def index(cls):
        '''Returns index kwargs used for collection index.'''
        return getattr(cls, "_index", None)

    @classmethod
    def collection(cls):
        '''Returns collection kwargs used for collection creation.'''
        return getattr(cls, "_collection", {"name": cls.__name__})

    @classmethod
    def dereference(cls, dbref):
        db = get_database()
        doc = db.dereference(dbref)
        doc_type = cls
        if not doc["_type"] == cls.__name__:
            for subc in rget_subclasses(cls):
                if doc["_type"] == subc.__name__:
                    doc_type = subc
        if dbref.id in doc_type.__cache__:
            document = doc_type.get_cache(doc["_id"])
            document.data = doc
        else:
            document = doc_type(**doc)
        return document
