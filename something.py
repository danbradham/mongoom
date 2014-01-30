class IAddObj(object):

    def __init__(self, parent):
        self._parent = parent

    def __str__(self):
        return self._parent.__str__()

    def __getattr__(self, name):
        return self.__dict__.get(name, self._parent.__getattr__(name))

    def __add__(self, value):
        return self._parent + value + 2


class TestObj2(object):
    def __init__(self):
        self._data = {"x": 0}
        self._x = IAddObj(self._data["x"])

    @property
    def x(self):
        return self._data["x"]

    @x.setter
    def x(self, value):
        self._data["x"] = value

o = TestObj2()
print o._data
print o.x

o.x = o.x + 5
print o.x
print o._data

o.x += 5
print o.x

b = {"thing": o.x}
print b

print type(o.x)
