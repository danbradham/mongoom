from copy import copy


class ListFieldProxy(object):
    '''A proxy object for a __get__ call to a ListField. Provides a typical
    list interface for ListField descriptors. Redirects all getattrs to a
    parent_list. The parent_list is always a list in a Documents _data dict.'''

    def __init__(self, parent_list, parent):
        self._list = parent_list

    def __str__(self):
        return self._list.__str__()

    def __getattr__(self, name):
        return self.__dict__.get(name, getattr(self._list, name))


class ListField(object):

    def __init__(self, *_types, **kwargs):
        self._types = _types
        self.name = kwargs.get("name", list)
        self.default = kwargs.get("default", list)
        self.required = kwargs.get("required", list)

    def __get__(self, inst, cls):
        list_proxy = ListFieldProxy(
            inst._data[self.name],
            inst)
        return list_proxy

    def __set__(self, inst, value):
        inst._data[self.name] = value


class Document(object):

    field = ListField()

    def __init__(self):
        self._data = {"_type": self.__class__}
        for k, v in self.__class__.__dict__.iteritems():
            if isinstance(v, ListField):
                setattr(v, "name", k)
                setattr(self, k, [])


def main():
    from pprint import pprint
    doc_a = Document()

    doc_a.field.append(2)
    pprint(doc_a._data)

    doc_a.field.extend([2, 4, 6])
    pprint(doc_a._data)

    doc_a.field.append(2)
    pprint(doc_a._data)

    doc_a.field.remove(2)
    pprint(doc_a._data)

    print doc_a.field
    print type(doc_a.field)

if __name__ == '__main__':
    main()
