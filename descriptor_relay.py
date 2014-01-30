class Loopback(object):
    '''Loops all getattr calls back to parent.'''

    def __init__(self, value, parent):
        self.p = parent
        self.v = value

    def __str__(self):
        return self.v.__str__()

    def __getattr__(self, name):
        return getattr(self.p, name, getattr(self.v, name))


class Descriptor(object):

    def __init__(self, *_types, **kwargs):
        self._types = _types
        self.required = kwargs.get("required", None)
        self.default = kwargs.get("default", None)
        self.name = kwargs.get("name", None)

    def __get__(self, inst, cls):
        return Loopback(inst._data[self.name], self)

    def __set__(self, inst, value):
        inst._data[self.name] = value


class Document(object):

    field = Descriptor()

    def __init__(self):
        self._data = {"_type": self.__class__}
        for k, v in self.__class__.__dict__.iteritems():
            if isinstance(v, Descriptor):
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
