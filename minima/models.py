from mongorm import Document, Field, ListField
from bson import DBRef


class User(Document):
    username = Field(str)
    password = Field(str)


class Comment(Document):
    user = Field(DBRef, required=True)



class StandardDoc(Document):
    image = Field(str)
    name = Field(str, required=True)
    status = Field(int)
    user = Field(DBRef, required=True)
    comments = ListField(DBRef)
    checklists = ListField(DBRef)
    references = ListField(DBRef)


class Project(StandardDoc):
    """Project Model"""


class Sequence(StandardDoc):
    """Sequence Model"""


class Shot(StandardDoc):
    """Shot Model"""


class Version(Document):
    name = Field(str)
    images = ListField(str)
    videos = ListField(str)
    filepath = Field(str)
    user = Field(DBRef)
    comments = ListField(DBRef)


class Component(Document):
    name = Field(str, required=True)
    status = Field(int)
    user = Field(str)
    versions = ListField(DBRef)
    comments = ListField(DBRef)

    def increment(self, *args, **kwargs):
        v_index = 1 if not hasattr(self, "versions") else len("versions")
        v_name = "v{0:0>3d}".format(v_index)
        kwargs["name"] = v_name
        kwargs["_parent"] = self.ref
        v = Version(*args, **kwargs)
        v.save()
        self.versions.append(v.ref)
        return v

    def publish(self, *args, **kwargs):
        v_name = "master"
        kwargs["name"] = v_name
        kwargs["_parent"] = self.ref
        v = Version(*args, **kwargs)
        self.versions.append(v.ref)
        return v
