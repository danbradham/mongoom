from pymongo import MongoClient

CONNECTION = None


class CustomDict(dict):

    def __init__(self, *args, **kwargs):
        super(CustomDict, self).__init__(*args, **kwargs)
        self._type = self.__class__.__name__

    def __setattr__(self, attr, value):
        self[attr] = value

    def __getattr__(self, attr):
        if not hasattr(self, attr):
            return self[attr]
        super(CustomDict, self).__getattribute__(attr)

    def save(self):
        global CONNECTION
        if not CONNECTION:
            connect()

        self._id = CONNECTION[self._type].insert(self)


def connect():

    global CONNECTION
    conn = MongoClient()
    db = conn.test_db
    CONNECTION = db


if __name__ == "__main__":
    obj = CustomDict(
        name="right",
        funk="left",
        punk=["left", "right"])

    obj2 = CustomDict(
        name="embeds right",
        embed=obj)

    print obj
    print obj2

    # obj2.save()
