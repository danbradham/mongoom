from mongorm import *
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

    connect("test_api", "localhost", 27017)
    c = get_connection()
    c.drop_database("test_api")


    frank = User(
        name="Frank",
        last_name="Footer").save()

    asset_a = Container(
        name="Asset A",
        user=frank).save()

    pprint(asset_a._data, width=1)

    model_a = Component(
        name="Awesome Model",
        user=frank).save()

    master = Version(
        name="master",
        user=frank,
        path="path/to/file.ma").save()

    asset_a.components += model_a  # == asset_a.children.append(model_a)
    model_a.versions += master  # == model_a.versions.append(master)

    pprint(asset_a._data, width=1)

    asset_a.save()
    model_a.save()
    master.save()

if __name__ == "__main__":
    main()
