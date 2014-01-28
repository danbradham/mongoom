from pymongo import MongoClient

CONNECTION = None


class BaseField(object):
    pass


class Field(BaseField):
    pass


class ListField(BaseField):
    pass


class MetaDoc(type):

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
                yield cls(**doc)

        cls_attrs["objects"] = property(objects)

        return super(MetaDoc, cls).__new__(cls, clsname, bases, cls_attrs)

    def __init__(self, name, bases, attrs):
        super(MetaDoc, self).__init__(name, bases, attrs)
        self.type = name


class BaseDocument(dict):

    __metaclass__ = MetaDoc

    def __init__(self, *args, **kwargs):
        super(BaseDocument, self).__init__(*args, **kwargs)
        self._type = self.__class__.__name__

    def __setattr__(self, attr, value):
        if attr.startswith("__"):
            setattr(self, attr,  value)
        else:
            self[attr] = value

    def __getattr__(self, attr):
        if not hasattr(self, attr) and not attr.startswith("__"):
            return self[attr]
        super(BaseDocument, self).__getattribute__(attr)

    def save(self):
        global CONNECTION
        if not CONNECTION:
            connect()

        self._id = CONNECTION[self._type].insert(self)


class Document(BaseDocument):
    pass


class EmbeddedDocument(BaseDocument):

    def __init__(self, parent):
        self.__parent = parent

    def save(self):
        self.__parent.save()


def connect():

    global CONNECTION
    conn = MongoClient()
    db = conn.test_db
    CONNECTION = db


if __name__ == "__main__":



    obj = Document(
        name="right",
        funk="left",
        punk=["left", "right"])

    obj2 = EmbeddedDocument(
        name="embeds right",
        embed=obj)

    print obj
    print obj2

    obj.save()
    obj2.save()
