from nose.tools import ok_, eq_, raises
from pymongorm import (Document, Field, ListField, connect, get_connection,
                       get_database, ValidationError)
from bson.objectid import ObjectId
from datetime import datetime

connect("test_db", "localhost", 27017)


class User(Document):
    _index = {"key_or_list": [("name", 1), ("last_name", 1)], "unique": True}
    name = Field(basestring, required=True)
    last_name = Field(basestring, required=True)
    created = Field(datetime, default=datetime.utcnow)


class Version(Document):
    name = Field(basestring)
    user = Field(User)
    path = Field(basestring)
    images = ListField(basestring)
    modified = Field(datetime, default=datetime.utcnow)


class Component(Document):
    _index = {"key_or_list": [("name", 1), ("created", 1)], "unique": True}
    name = Field(basestring)
    user = Field(User)
    created = Field(datetime, default=datetime.utcnow)
    versions = ListField(Version)


class Container(Document):
    _index = {"key_or_list": [("name", 1), ("created", 1)], "unique": True}
    name = Field(basestring, required=True)
    user = Field(User)
    created = Field(datetime, default=datetime.utcnow)
    components = ListField(Component)
    images = ListField(basestring)


def test_connect():
    '''Connection'''
    c = get_connection()
    c.drop_database("test_db")

    eq_(get_database(), c.test_db)

    c.test_db.test_col.insert({"name": "test_entry"})
    doc = c.test_db.test_col.find_one({"name": "test_entry"})
    ok_(all(field in doc for field in ["_id", "name"]))


def test_save():
    '''Save Document'''
    c = get_connection()
    c.drop_database("test_db")

    frank = User(
        name="Frank",
        last_name="Footer")

    eq_(frank.data["name"], "Frank")
    eq_(frank.data["last_name"], "Footer")
    ok_("created" in frank.data)
    ok_("_id" not in frank.data)

    frank.save()
    ok_(isinstance(frank._id, ObjectId))

    frank.last_name = "Footers"
    frank.save()


def test_find_one():
    '''Find One'''
    c = get_connection()
    c.drop_database("test_db")

    c.test_db.User.insert({"name": "Frank", "last_name": "Footer"})

    frank = User.find_one(name="Frank")

    ok_(isinstance(frank._id, ObjectId))


def test_find():
    '''Find'''
    c = get_connection()
    c.drop_database("test_db")

    frank = User(
        name="Frank",
        last_name="Footer"
        ).save()

    bob = User(
        name="Bob",
        last_name="Oob"
        ).save()

    sam = User(
        name="Sam",
        last_name="Samuelson"
        ).save()

    users = User.find()
    ok_(all(user in [frank, bob, sam]) for user in users)


@raises(ValidationError)
def test_missing_required():
    '''Missing Required Field'''
    c = get_connection()
    c.drop_database("test_db")

    #Try to save while missing a required field (last_name)
    User(name="Frank").save()


def test_RefField():
    '''RefField'''
    from pprint import pprint
    c = get_connection()
    c.drop_database("test_db")

    frank = User(
        name="Frank",
        last_name="Footer"
        ).save()

    asset_a = Container(
        name="Asset A",
        user=frank)

    ok_(asset_a.user is frank)


def test_ListField():
    '''ListField'''
    c = get_connection()
    c.drop_database("test_db")

    frank = User(
        name="Frank",
        last_name="Footer"
        ).save()

    project_a = Container(
        name="Project A",
        user=frank)

    project_a.images.append("path/to/image")
    project_a.images.extend(["path/to/image2", "path/to/image3"])
    eq_(project_a.images.value,
        ["path/to/image", "path/to/image2", "path/to/image3"])
    eq_(project_a.images[0], "path/to/image")
    eq_(project_a.images[-1], "path/to/image3")
    eq_(project_a.images[1:], ["path/to/image2", "path/to/image3"])


def test_ListRefField():
    '''ListRefField'''
    c = get_connection()
    c.drop_database("test_db")

    frank = User(
        name="Frank",
        last_name="Footer"
        ).save()

    asset_a = Container(
        name="Asset A",
        user=frank).save()

    model_a = Component(
        name="Awesome Model",
        user=frank).save()

    master = Version(
        name="master",
        user=frank,
        path="path/to/file.ma").save()

    v001 = Version(
        name="v001",
        user=frank,
        path="path/to/file.ma").save()

    asset_a.components += model_a
    model_a.versions += master, v001

    asset_a.save()
    model_a.save()

    ok_(all(isinstance(v, Version) for v in model_a.versions))
    ok_(all(isinstance(c, Component) for c in asset_a.components))


def test_index():
    db = get_database()
    index_kwargs = User.index()
    index_name = "_".join(
        [str(item) for key in index_kwargs["key_or_list"] for item in key])
    ok_(index_name in db.User.index_information())
