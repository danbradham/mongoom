from bson.objectid import ObjectId
from bson import DBRef
from collections import Iterable
import sys


class ValidationError(Exception):
    pass


class BaseField(object):
    '''
    A descriptor that sets and gets data from the _data dict of an object. The
    name attribute is set in the metaclass of Document, MetaDocument. BaseField
    should only be used as a Baseclass. Use Field for a basic Field descriptor.

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


# Use Field not BaseField for clarity. Use BaseField only as a super.
Field = type("Field", (BaseField,), {})


class RefField(BaseField):

    def __init__(self, *types, **kwargs):
        self.doc_types = dict((typ.__name__, typ) for typ in types)
        super(RefField, self).__init__(DBRef, **kwargs)

    def __get__(self, inst, cls):
        if inst:
            ref = inst._data[self.name]
            doc_type = self.doc_types.get(
                ref.collection,
                getattr(sys.modules["__main__"], ref.collection, None))
            return doc_type.dereference(ref)
        return self

    def __set__(self, inst, value):
        try:
            self.validate(value)
        except ValidationError:
            value = value.ref
        inst._data[self.name] = value


class ObjectIdField(BaseField):

    def __init__(self, *types, **kwargs):
        super(ObjectIdField, self).__init__(ObjectId, **kwargs)


class SelfishField(BaseField):
    '''A very selfish descriptor. Returns itself on __get__ redirecting attr
    lookup back to itself. Not entirely selfish though, __getattr__ is
    overloaded to return attribute lookup back to its _value object.'''

    def __init__(self, *types, **kwargs):
        super(SelfishField, self).__init__(*types, **kwargs)
        self._value = None

    def __getattr__(self, name):
        return getattr(self._value, name)

    def __get__(self, inst, cls):
        if inst:
            self._value = inst._data[self.name]
        return self

    def __set__(self, inst, value):
        self._value = value
        inst._data[self.name] = value


class ListField(SelfishField):
    '''A descriptor that '''

    def __init__(self, *types, **kwargs):
        kwargs["default"] = list
        super(ListField, self).__init__(*types, **kwargs)

    def __set__(self, inst, value):
        if not isinstance(value, list):
            raise ValidationError("Must be a list.")
        for item in value:
            self.validate(item)
        self._value = value
        inst._data[self.name] = value

    def __getitem__(self, key):
        return self._value[key]

    def __setitem__(self, key, value):
        self.validate(value)
        self._value[key] = value
        return self._value

    @property
    def value(self):
        return self._value


class ListRefField(ListField):

    def __init__(self, *types, **kwargs):
        self.doc_types = dict((typ.__name__, typ) for typ in types)
        super(ListRefField, self).__init__(DBRef, **kwargs)

    def __setitem__(self, key, value):
        if not value in self.types:
            value = value.ref
        super(ListRefField, self).__setitem__(key, value)

    def __getitem__(self, key):
        ref = self._value[key]
        doc_type = self.doc_types.get(
            ref.collection,
            getattr(sys.modules["__main__"], ref.collection, None))
        return doc_type.dereference(ref)

    def __iadd__(self, value):
        if isinstance(value, Iterable):
            self.extend(value)
            return self._value
        self.append(value)
        return self._value

    def __add__(self, value):
        self.append(value)
        return self._value

    def append(self, value):
        try:
            self.validate(value)
        except ValidationError:
            value = value.ref
        self._value.append(value)

    def extend(self, values):
        for value in values:
            self.append(value)
