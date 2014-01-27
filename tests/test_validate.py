from nose.tools import *
from mongorm import Document, Field, ListField, ValidationError


class Component(Document):

    name = Field(str, required=True)
    image = Field(str)
    published = Field(bool, required=True, default=True)
    versions = ListField(str, required=True)
    years = ListField(int)


@raises(ValidationError)
def test_list_field_mixed():
    comp = Component(name="Frank", versions=["a", 1, 2])
    comp.save()


def test_list_field_int():
    comp = Component(name="Frank", versions=["a"], years=[1987, 1988, 2014])
    comp.save()
    eq_(comp.years, [1987, 1988, 2014])


def test_should_validate():
    comp = Component(name="Frank", versions=["a", "b", "c"])
    comp.save()
    eq_(comp.name, "Frank")
    eq_(comp.versions, ["a", "b", "c"])


@raises(ValidationError)
def test_raise_validate():
    comp = Component()
    comp.save()


def test_default():
    comp = Component(name="Frank", versions=["a"])
    comp.save()
    eq_(comp.published, True)
