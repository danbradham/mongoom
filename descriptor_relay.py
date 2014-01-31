class Field(object):
    '''
    A descriptor whose __get__ method returns an instance of Loopback. Loopback
    objects redirect all attribute lookup back to their parent descriptor.
    '''

    def __init__(self, name):
        self.name = name
        self.value = None

    def __get__(self, inst, cls):
        self.value = inst._data[self.name]
        return self

    def __set__(self, inst, value):
        inst._data[self.name] = value

    def __getattr__(self,)

class Document(object):
    def __init__(self, **fields):
        self._data = {"_type": self.__class__.__name__}
        for name, value in fields.iteritems():
            setattr(self, name, value)


class User(Document):
    username = Field("username")
    password = Field("password")


def main():
    from pprint import pprint
    teddy = User(
        username="Teddy",
        password="Roosevelt"
        )

    print teddy.username == "Teddy"
    print type(teddy.username)

    print teddy.username.value == "Teddy"

if __name__ == '__main__':
    main()
