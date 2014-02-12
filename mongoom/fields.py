from bson.objectid import ObjectId
from bson import DBRef
from collections import Iterable
import sys
from .utils import is_document, is_embedded


class ValidationError(Exception):
    pass


class BaseField(object):
    '''A descriptor that sets and gets data from the _data dict of an
    object. The name attribute is set in the metaclass of Document,
    MetaDocument. BaseField should only be used as a Baseclass. Use
    :class:`Field` for a basic Field descriptor.

    :param types: all args are types for validation
    :param default: default values are copied to inst._data on
           instantiation, can be a callable.
    :param required: is the field requried?
    :param name: name of the attribute that field is assigned to.
        (When used in classes inheriting from Document, you don't need to set
         the name parameter.)
    '''

    def __init__(self, *types, **kwargs):
        self.name = kwargs.get("name")
        self.types = types
        self.default = kwargs.get("default", None)
        self.required = kwargs.get("required", False)

    def __repr__(self):
        fmt = ("<{name}(name={name}, types={types}, "
               "default={default}, required={required})>")
        return fmt.format(**self.__dict__)

    def __get__(self, inst, cls):
        if inst:
            return inst._data[self.name]
        return self

    def __set__(self, inst, value):
        self.validate(value)
        inst._data[self.name] = value

    def validate(self, value):
        if not isinstance(value, self.types):
            raise ValidationError(
                "{} must be of types: {}.".format(self.name, self.types))

    def to_dict(self, value):
        '''Make sure that the value is a dictionary. If value is an
        :class:`EmbeddedDocument`, pull the documents data.'''

        if not isinstance(value, dict):
            value = value.data
        return value

    def to_ref(self, value):
        '''Make sure that the value is a :class:`bson.dbref.DBRef`. If value is a
        :class:`Document` object, pull the documents ref.'''

        if not isinstance(value, DBRef):
            value = value.ref
        return value

    def from_dict(self, value):
        '''Decodes a dict object to an :class:`EmbeddedDocument`.'''

        if "_type" in value:
            doc_type = self.doc_types.get(
                value["_type"],
                getattr(sys.modules["__main__"], value["_type"], None))
            return doc_type(use_data=value)
        return value

    def from_ref(self, value):
        '''Returns a :class:`Document` from a :class:`bson.dbref.DBRef`.'''

        doc_type = self.doc_types.get(
            value.collection,
            getattr(sys.modules["__main__"], value.collection, None))
        return doc_type.dereference(value)


class Field(BaseField):
    '''A multipurpose field supporting python standard types. This is the
    go to field for basestring, boolean, int, float, dict and also
    supports :class:`Document`, and :class:`EmbeddedDocument`.
    :class:`Document` objects are automatically stored as
    :class:`bson.dbref.DBRef` and decoded back to :class:`Document`. Similarly
    :class:`EmbeddedDocument` objects are stored as dicts and decoded back to
    :class:`EmbeddedDocument`.

    :param types: all args are types for validation
    :param default: default values are copied to inst._data on
        instantiation, can be a callable.
    :param required: is the field requried?
    :param name: name of the attribute that field is assigned to. (When
        used in classes inheriting from Document, you don't need to set
        the name parameter.)
    '''

    def __init__(self, *types, **kwargs):
        self.encode, self.decode = None, None
        self.doc_types = dict((typ.__name__, typ) for typ in types)
        if all(is_document(typ) for typ in types):
            self.encode = self.to_ref
            self.decode = self.from_ref
            types = (DBRef, )
        elif all(is_embedded(typ) for typ in types):
            self.encode = self.to_dict
            self.decode = self.from_dict
            types = (dict, )
        super(Field, self).__init__(*types, **kwargs)

    def __get__(self, inst, cls):
        if self.decode and inst:
            return self.decode(inst._data[self.name])
        super(Field, self).__get__(inst, cls)

    def __set__(self, inst, value):
        if self.encode:
            value = self.encode(value)
        super(Field, self).__set__(inst, value)


class ObjectIdField(BaseField):
    '''Exactly the same as :class:`Field`(ObjectId)'''

    def __init__(self, **kwargs):
        super(ObjectIdField, self).__init__(ObjectId, **kwargs)


class SelfishField(BaseField):
    '''A very selfish descriptor. Returns itself on __get__ redirecting
    attr lookup back to itself, allowing us to "overload" methods and add
    custom functionality. If the attribute or method is not found in the
    descriptor, attribute lookup is directed back toward the data
    object that we're acting on. One drawback is that we always return a
    descriptor object on lookup and not a standard python object. To access
    the underlying python object the value property has been introduced.'''

    def __init__(self, *types, **kwargs):
        self._value = None
        super(SelfishField, self).__init__(*types, **kwargs)

    def __getattr__(self, name):
        return getattr(self._value, name)

    def __get__(self, inst, cls):
        if inst:
            self._value = inst._data[self.name]
        return self

    def __set__(self, inst, value):
        self._value = value
        inst._data[self.name] = value

    @property
    def value(self):
        return self._value


class ListField(SelfishField):
    '''A :class:`ListField`! Supports multiple types like a :class:`Field`
    descriptor, and the same automatic encoding and decoding of
    :class:`bson.dbref.DBRef` and :class:`EmbeddedDocument`.

    :param types: all args are types for validation
    :param default: default values are copied to inst._data on
        instantiation, can be a callable.
    :param required: is the field requried?
    :param name: name of the attribute that field is assigned to. (When
        used in classes inheriting from Document, you don't need to set
        the name parameter.)
    '''

    def __init__(self, *types, **kwargs):
        kwargs["default"] = list
        self.encode, self.decode = None, None
        self.doc_types = dict((typ.__name__, typ) for typ in types)
        if all(is_document(typ) for typ in types):
            self.encode = self.to_ref
            self.decode = self.from_ref
        elif all(is_embedded(typ) for typ in types):
            self.encode = self.to_dict
            self.decode = self.from_dict
        super(ListField, self).__init__(list, **kwargs)

    def __set__(self, inst, value):
        self.validate(value)
        items = []
        for item in value:
            if self.encode:
                item = self.encode(item)
            items.append(item)
        self._value = items
        inst._data[self.name] = items

    def __getitem__(self, key):
        value = self._value[key]
        if self.decode:
            value = self.decode(value)
        return value

    def __setitem__(self, key, value):
        if self.encode:
            value = self.encode(value)
        self._value[key] = value
        return self._value

    def __iadd__(self, value):
        if isinstance(value, Iterable):
            self.extend(value)
            return self._value
        self.append(value)
        return self._value

    def __add__(self, value):
        if isinstance(value, Iterable):
            self.extend(value)
            return self._value
        raise TypeError("Can not concatenate list and {}".formate(type(value)))

    def append(self, value):
        if self.encode:
            value = self.encode(value)
        self._value.append(value)

    def extend(self, values):
        for value in values:
            self.append(value)
