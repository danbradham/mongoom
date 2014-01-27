from pymongo import MongoClient

CONNECTION = None


class CustomDict(dict):

    def __init__(self, *args, **kwargs):
        super(CustomDict, self).__init__(*args, **kwargs)
        self._type = self.__class__
        self.__dict__.update(self)

    def __setattr__(self, attr, value):
        self[attr] = value
        super(CustomDict, self).__setattr__(attr, value)

    def __getattr__(self, attr, value):
        if not hasattr(self, attr):
            return self.get(attr)
        super(CustomDict, self).__getattribute__(attr, value)

    def save(self):
        global CONNECTION
        if not CONNECTION:
            connect()

        self._id = CONNECTION[self._type].insert()


def connect():

    global CONNECTION
    conn = MongoClient()
    db = conn.test_db
    CONNECTION = db


if __name__ == "__main__":
    # db = connect()

    obj = CustomDict({"hello": "old pal"})
    print obj
    print obj.__dict__
    obj.name = "funk"
    print obj
    print obj.__dict__
    # db.custom_dict.insert(obj)
