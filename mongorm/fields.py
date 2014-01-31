from bson.objectid import ObjectId
from bson import DBRef
from .utils import dereference


class ValidationError(Exception):
    pass


class BaseField(object):
    '''
    A descriptor whose __get__ method returns an instance of Loopback. Loopback
    objects redirect all attribute lookup back to their parent descriptor. This
    allows you to call methods on a descriptor from their parent instance.

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
        self.types = (types if not str in types
                      else tuple(list(types) + [unicode]))
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
        if not type(value) in self.types:
            raise ValidationError(
                "{} must be of types: {}.".format(self.name, self.types))


class Field(BaseField):
    pass


class RefField(BaseField):

    def __init__(self, *types, **kwargs):
        super(RefField, self).__init__(DBRef, **kwargs)

    def __get__(self, inst, cls):
        if inst:
            return dereference(inst._data[self.name])
        return self

    def __set__(self, inst, value):
        if not value in self.types:
            value = value.ref
        inst._data[self.name] = value


class ObjectIdField(BaseField):

    def __init__(self, *types, **kwargs):
        super(ObjectIdField, self).__init__(ObjectId, **kwargs)


class SelfishField(BaseField):
    '''A very selfish descriptor. Returns itself on __get__ redirecting attr
    lookup back to itself. Not entirely selfish though, __getattr__ is
    overloaded to return attribute lookup back to its _value object.'''

    def __init__(self, name):
        self.name = name
        self._value = None

    def __getattr__(self, name):
        return getattr(self._value, name)

    def __get__(self, inst, cls):
        if inst:
            self._value = inst.__dict__[self.name]
        return self

    def __set__(self, inst, value):
        self._value = value
        inst.__dict__[self.name] = value


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
        super(ListRefField, self).__init__(DBRef, **kwargs)

    def __setitem__(self, key, value):
        if not value in self.types:
            value = value.ref
        super(ListRefField, self).__setitem__(key, value)

    def __getitem__(self, key):
        value = self._value[key]
        value = dereference(value)
        return value

    def __iadd__(self, value):
        self.append(value)
        return self._value

    def __isub__(self, value):
        self._value.remove(value)
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
