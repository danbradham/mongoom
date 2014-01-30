from copy import copy
from bson.objectid import ObjectId
from bson import DBRef
from .utils import dereference


class ValidationError(Exception):
    pass


class BaseField(object):
    '''Defines a basic interface for all fields. Fields are descriptors used
    as class attributes on Document objects to define their schema. A field is
    validated each time it is set.'''

    def __init__(self, *types, **kwargs):
        '''
        :param types: all args are types for validation
        :param default: default values are copied to inst._data on
               instantiation, can be a callable.
        :param required: is the field requried?
        :param name: name of the attribute that field is assigned to.
            (In most cases you don't need to pass this kwarg)
        '''

        self._types = (types if not str in types
                       else tuple(list(types) + [unicode]))
        self.default = kwargs.get("default", None)
        self.required = kwargs.get("required", False)
        self.name = kwargs.get("name", None)

    def __get__(self, inst, cls):
        defl = (copy(self.default) if not callable(self.default)
                else self.default())
        return inst._data.setdefault(self.name, defl)

    def __set__(self, inst, value):
        self.validate(value)
        inst._data[self.name] = value

    def validate(self, value):
        if type(value) in self._types:
            return True
        raise ValidationError(
            "{} : {} not in {}".format(self.name, value, self._types))


class Field(BaseField):
    pass


class ObjectIdField(BaseField):

    def __init__(self, *types, **kwargs):
        types = types if types else (ObjectId,)
        super(ObjectIdField, self).__init__(*types, **kwargs)


class RefField(BaseField):

    def __init__(self, *types, **kwargs):
        types = types if types else (DBRef,)
        super(RefField, self).__init__(*types, **kwargs)

    def __get__(self, inst, cls):
        return dereference(inst._data[self.name])

    def __set__(self, inst, value):
        try:
            self.validate(value)
        except ValidationError:
            value = value.ref
            self.validate(value)
        inst._data[self.name] = value


class ListFieldProxy(object):
    '''A proxy object for a __get__ call to a ListField. Provides a typical
    list interface for ListField descriptors. Redirects all getattrs to a
    parent_list. The parent_list is always a list in a Documents _data dict.'''

    def __init__(self, parent_list, parent):
        self._list = parent_list
        self._parent = parent

    def __getattr__(self, name):
        return self.__dict__.get(name, self._list.__getattr__(name))

    def __iadd__(self, value):
        self.append(value)


class ListRefFieldProxy(ListFieldProxy):
    '''A proxy object for a __get__ call to a ListRefField. Provides a typical
    list interface for ListRefField descriptors. The big benefit here is
    enabling auto-referencing and dereferencing for Document subclasses'''

    def __getitem__(self, index):
        value = self._list[index]
        if isinstance(value, DBRef):
            return dereference(value)
        return value

    def __setitem__(self, index, value):
        if not isinstance(value, DBRef):
            value.parent = self._parent
            value = value.ref
        self._list[index] = value

    def append(self, value):
        if not isinstance(value, DBRef):
            value.parent = self._parent
            value = value.ref
        self._list.append(value)


class ListField(BaseField):

    def __init__(self, *types, **kwargs):
        kwargs["default"] = list
        super(ListField, self).__init__(*types, **kwargs)

    def __get__(self, inst, cls):
        defl = (copy(self.default) if not callable(self.default)
                else self.default())
        list_proxy = ListFieldProxy(
            inst._data.setdefault(self.name, defl),
            inst)
        return list_proxy

    def __set__(self, inst, value):
        inst._data[self.name] = value

    def validate(self, value):
        for item in value:
            if not isinstance(value, self._types):
                raise ValidationError("Value in {} : {} not in {}".format(
                                      self.name, value, self._types))


class ListRefField(ListField):

    def __init__(self, *types, **kwargs):
        types = types if types else (DBRef,)
        super(ListRefField, self).__init__(*types, **kwargs)

    def __get__(self, inst, cls):
        defl = (copy(self.default) if not callable(self.default)
                else self.default())
        list_proxy = ListRefFieldProxy(
            inst._data.setdefault(self.name, defl),
            inst)
        return list_proxy
