from nose.tools import *
from mongorm import (Document, Field, ListField, RefField, ListRefField,
                     connect, get_connection, get_database)
from bson.objectid import ObjectId
from bson import DBRef
from datetime import datetime


class User(Document):
    name = Field(str, required=True)
    last_name = Field(str, required=True)
    created = Field(datetime, default=datetime.utcnow)


class Version(Document):
    name = Field(str)
    user = RefField()
    path = Field(str)
    images = ListField(str)
    modified = Field(datetime, default=datetime.utcnow)
    parent = RefField()


class Component(Document):
    name = Field(str)
    user = RefField()
    created = Field(datetime, default=datetime.utcnow)
    versions = ListRefField()
    parent = RefField()


class Container(Document):

    name = Field(str, required=True)
    user = RefField()
    created = Field(datetime, default=datetime.utcnow)
    components = ListRefField()
    images = ListField()


def test_connect():
    '''Requires mongod to be running on localhost'''

    connect("test_db", "localhost", 27017)
    c = get_connection()
    c.drop_database("test_db")

    eq_(get_database(), c.test_db)

    c.test_db.test_col.insert({"name": "test_entry"})
    doc = c.test_db.test_col.find_one({"name": "test_entry"})

    eq_(doc, {"name": "test_entry"})


def test_save():

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

    c = get_connection()
    c.drop_database("test_db")

    c.test_db.User.insert({"name": "Frank", "last_name": "Footer"})

    frank = User.find_one(name="Frank")

    ok_(isinstance(frank._id, ObjectId))


def test_find():

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
    for user in users:
        ok_(user in [frank, bob, sam])  # check if returned object is in cache


@raises(ValidationError)
def test_missing_required():

    c = get_connection()
    c.drop_database("test_db")

    #Try to save while missing a required field (last_name)
    User(name="Frank").save()


def test_RefField():

    c = get_connection()
    c.drop_database("test_db")

    frank = User(
        name="Frank",
        last_name="Footer"
        ).save()

    asset_a = Container(
        name="Asset A",
        user=frank).save()

    ok_(asset_a.user is DBRef)


def test_ListField():

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
    project_a.images.value = ["path/to/image", "path/to/image2", "path/to/image3"]

    pprint(asset_a._data, width=1)

    model_a = Component(
        name="Awesome Model",
        user=frank).save()

    master = Version(
        name="master",
        user=frank,
        path="path/to/file.ma").save()

    print master.images
    print master.images.value
    master.images.append("path/to/image")
    master.images.append("path/to/another")

    asset_a.components.append(model_a)  # == asset_a.children.append(model_a)
    model_a.versions.append(master)  # == model_a.versions.append(master)

    for obj in asset_a.components:
        print obj

    print asset_a.components[0]

    print master.images[0]
    print master.images[1]
    master.images[0] = "path/to/something"
    print master.images[0]

    pprint(master.data, width=1)
    pprint(asset_a.data, width=1)
    asset_a.save()
    model_a.save()
    master.save()

if __name__ == "__main__":
    main()
