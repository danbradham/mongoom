import weakref
from bson import DBRef
from copy import copy
from functools import partial
from .connection import get_collection, get_database
from .utils import is_field
from .fields import ObjectIdField, ValidationError, BaseField
from .utils import rget_subclasses


def cache_ref_deleted(cls, wref):
    found = None
    for _id, ref in cls.__cache__.iteritems():
        if ref == wref:
            found = _id
            break
    cls.__cache__.pop(found)


class MetaDocument(type):
    '''Metaclass for all :class:`Document` objects. Automatically sets
    :class:`BaseField` name attributes to their referenced name.

    :attr _type: :class:`BaseField`(basestring, default=clsname)
    :attr _id: :class:`ObjectIdField`
    :attr __cache__: ObjectId to :class:`Document` object hash
    '''

    def __new__(cls, clsname, bases, attrs):
        attrs["_type"] = BaseField(basestring, default=clsname)
        attrs["_id"] = ObjectIdField()
        attrs["__cache__"] = {}
        for name, value in attrs.iteritems():
            if is_field(value):
                # Set each field's name attribute to their reference name
                value.__dict__["name"] = name

        return super(MetaDocument, cls).__new__(cls, clsname, bases, attrs)


class Document(object):
    '''A MongoDB document mapping. A Document's Schema is defined by it's
    class attributes that are Field instances.

    :param data: Field name, value pairs for a MongoDB document.

    Usage::

        class User(Document):
            name = Field(basestring)

        frank = User(name="Frank").save()
    '''

    __metaclass__ = MetaDocument

    def __init__(self, **data):
        if "_id" in data and not data["_id"] in self.__cache__:
            self.cache(data["_id"])  # Add instance to cache
        self._data = {}
        for name, value in data.iteritems():
            setattr(self, name, value)
        for name, field in self.fields.iteritems():
            if field.default is not None:
                defl = (copy(field.default) if not callable(field.default)
                        else field.default())
                self._data.setdefault(name, defl)

    @property
    def ref(self):
        '''Returns a DBRef, saves before returning if _id not in data.'''

        if not "_id" in self.data:
            self.save()
        return DBRef(self._type, self._id)

    @property
    def fields(self):
        '''Returns all fields from baseclasses to allow for field
        inheritence. Collects fields top down ensuring that fields are
        properly overriden by subclasses.
        '''

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
        '''Document cache, used to ensure that only one object mapped
        to a db document is in memory at any given time.
        '''

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
        '''Find objects in a classes collection.

        :param decode: If True, return :class:`Document` objects.
        :param spec: Key, Value pairs to match in mongodb documents.
        '''

        col = get_collection(cls.index(), cls.collection())
        docs = col.find(spec)
        if not decode:
            return docs
        return cls.generate_objects(docs)

    @classmethod
    def find_one(cls, decode=True, **spec):
        '''Find one object in a classes collection.

        :param decode: If True, return :class:`Document` object.
        :param spec: Key, Value pairs to match in mongodb documents.
        '''

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

    def remove(self):
        '''Remove self from mongodb.'''

        col = get_collection(self.index(), self.collection())
        if "_id" in self.data:
            col.remove({"_id": self._id})

    @classmethod
    def index(cls):
        ''':return: Keyword args used for collection index.'''

        return getattr(cls, "_index", None)

    @classmethod
    def collection(cls):
        ''':return: Keyword args used for collection creation.'''

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


class MetaEmbedded(type):
    '''Metaclass for all :class:`EmbeddedDocument` objects. Automatically
    sets :class:`BaseField` name attributes to their referenced name.

    :attr _type: :class:`BaseField`(basestring, default=clsname)
    '''

    def __new__(cls, clsname, bases, attrs):
        attrs["_type"] = BaseField(basestring, default=clsname)
        for name, value in attrs.iteritems():
            if is_field(value):
                value.__dict__["name"] = name

        return super(MetaEmbedded, cls).__new__(cls, clsname, bases, attrs)


class EmbeddedDocument(object):
    '''Baseclass for all embedded documents. Unlike :class:`Document`,
    :class:`EmbeddedDocument` does not:
        * have a cache
        * have an objectid
        * have save, find or remove methods...*yet*
        * map to a collection


    :param from: If provided it is assigned to the _data attribute of
        the new instance, ensuring that the object passed in is exactly the
        same object that EmbeddedDocument is acting on. Typically only passed
        when decoding an embedded document as in :class:`BaseField`'s
        :meth:`from_dict` method.

    Usage::

        class Comment(EmbeddedDocument):
            user = Field("Frank")
            text = Field(basestring)

        my_comment = Comment(user="Frank", text="Hello there.")
    '''

    __metaclass__ = MetaEmbedded

    def __init__(self, **data):
        self._data = data.pop("from", {})
        for name, value in data.iteritems():
            setattr(self, name, value)
        for name, field in self.fields.iteritems():
            if field.default is not None:
                defl = (copy(field.default) if not callable(field.default)
                        else field.default())
                self._data.setdefault(name, defl)

    @property
    def fields(self):
        '''Returns all fields from baseclasses to allow for field
        inheritence. Collects fields top down ensuring that fields
        are properly overriden by subclasses.'''

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

    def validate(self):
        '''Ensure all required fields are in data.'''
        missing_fields = []
        for name, field in self.fields.iteritems():
            if field.required and not field.name in self.data:
                missing_fields.append(field.name)

        if missing_fields:
            raise ValidationError(
                "{} missing fields: {}".format(self.name, missing_fields))
