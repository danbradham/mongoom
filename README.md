mongorm
=======

An Object-Relational Mapping for MongoDB. MongORM's highest priority is to be as pythonic as possible. Heavily inspired by Django and MongoEngine, but,
attempting to be more simple to use.

```python
from mongorm import Document, Field, RefField, ListRefField, connect
from datetime import datetime

class User(Document):
    name = Field(basestring, required=True)
    last_name = Field(basestring, required=True)
    created = Field(datetime, default=datetime.utcnow)

class Comment(Document):
    user = RefField(user, required=True)
    text = Field(basestring, required=True)
    created = Field(datetime, default=datetime.utcnow)

class Project(Document):
    name = Field(basestring, required=True)
    user = RefField(User, required=True)
    created = Field(datetime, default=datetime.utcnow)
    description = Field(basestring)
    comments = ListRefField(Comment)

if __name__ == "__main__":
    connect("test_db", "localhost", 27017)

    edison = User(name="Thomas", last_name="Edison").save()
    bulb = Project(
        name="Light Bulb",
        user=edison,
        description="Create a commercially viable light bulb.",
        ).save()

    naysayer = User(name="Anonymous", last_name="Naysayer").save()
    rude_comment = Comment(
        user=naysayer,
        text=("It's impossible to create a viable light bulb. Like all of"
              "Mr. Edison's ideas, this too will be proven impracticle")
        ).save()

    bulb.comments += rude_comment
    bulb.save()

```
