from mongorm import *
from bson import DBRef
from bson.objectid import ObjectId
from datetime import datetime


class User(Document):
    name = Field(str)
    last_name = Field(str)


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


def main():
    from pprint import pprint

    me = User(
        name="Dan",
        last_name="Bradham",
        _id=ObjectId.from_datetime(datetime.utcnow())
        )
    pprint(me._data, indent=4, width=40)

    asset_a = Container(
        name="Asset A",
        user=me.ref,
        )
    pprint(asset_a._data, indent=4, width=40)

    # model_a = Component(
    #     name="Model A",
    #     user=me.ref,
    #     parent=asset_a,
    #     )

    # master = Version(
    #     name="master",
    #     user=me.ref,
    #     path="path/to/file.ma",
    #     images=["path/to/imagefile.png"],
    #     parent=model_a,
    #     )

    # model_a.versions.append(master)

    # print asset_a
    # print model_a
    # print master

if __name__ == "__main__":
    main()
