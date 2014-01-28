import sys
from datetime import datetime
from bson import DBRef
from .fields import BaseField, ListField, Field, ValidationError
from .utils import setdefaultattr
from .connect import get_connection


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


class MetaDoc(type):
    '''Base type for all documents. Remove class attributes of subclass
    BaseField and add them to a class attribute named fields. The fields dict
    can be used to validate documents to be '''

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
                yield decode(doc)

        cls_attrs["objects"] = property(objects)
        cls_attrs["_type"] = clsname

        return super(MetaDoc, cls).__new__(cls, clsname, bases, cls_attrs)


class BaseDocument(dict):
    __metaclass__ = MetaDoc

    _created = Field(datetime)
    _date = Field(datetime)

    def __init__(self, *args, **kwargs):
        super(BaseDocument, self).__init__(*args, **kwargs)
        self._type = self._type
        self._created = datetime.utcnow()
        self.__db = get_connection()

    def __setattr__(self, attr, value):
        if attr.startswith("__"):
            super(BaseDocument, self).__setattr__(attr, value)
        else:
            self.__setitem__(value)

    def __getattr__(self, attr):
        if attr.startswith("__"):
            return super(BaseDocument, self).__getattribute__(attr)
        return self.__getitem__(attr)

    def remove(self):
        if self._id:
            self.__db["_type"].remove({"_id": self._id})

    def save(self, validate=True, *args, **kwargs):
        self._date = datetime.utcnow()
        if validate:
            self.validate()
        if not hasattr(self, "_id"):
            self._id = self.__db[self.type].insert(self)
            return
        self.__db[self.type].update({"_id": self._id}, self)

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
    def find(cls, **spec):
        doc = cls.db[cls.type].find_one(spec)
        return decode(doc)


class Document(BaseDocument):

    _children = ListField(DBRef)
    _parent = Field(DBRef)

    def __iadd__(self, document):
        setdefaultattr(self, "_children", []).append(document.ref)
        setdefaultattr(document, "_parent", self.ref)

    def __isub__(self, document):
        self._children.remove(document.ref)
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
    def children(self):
        for child in self._children:
            doc = self.__db.dereference(child)
            yield decode(doc)

    @property
    def parent(self):
        doc = self.__db.dereference(self.parent)
        return decode(doc)
