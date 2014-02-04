mongorm
=======

An Object-Relational Mapping for MongoDB. MongORM's highest priority is to be as pythonic as possible. Heavily inspired by Django and MongoEngine, but,
attempting to be a bit easier to use. Here's a rather elaborate example of the core functionality:

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

    edison = User(
        name="Thomas",
        last_name="Edison",
        ).save()

    bulb = Project(
        name="Light Bulb",
        user=edison,
        description="Create a commercially viable light bulb.",
        ).save()

    naysayer = User(
        name="Anonymous",
        last_name="Naysayer",
        ).save()

    rude_comment = Comment(
        user=naysayer,
        text=("It's impossible to create a viable light bulb. Like all of"
              "Mr. Edison's ideas, this too will be proven impracticle"),
        ).save()

    bulb.comments += rude_comment
    bulb.save()

```

Also included with MongORM is an Event and Subscriber. Event objects are nothing more than a Document object residing in a capped collection. While subscribers are tailable cursors awaiting data to be entered into a capped collection. Using these two objects we can easily create a simple event handling system:

```python
from mongorm import Event, fire, Subscriber

class Create(Event):
    '''Create Event'''

class EventHandler(Subscriber):
    def handle(self, document):
        print document
        print document.ref.data

if __name__ == "__main__":
    connect("test_db")

    fire(Event)  # Fire a blank Event to initialize capped collection

    idiot = Comment(
        user=User.find_one(name="naysayer"),
        text="I feel like an idiot, the light bulb turned out great."
        ).save()
    bulb = Project.find_one(name="Light Bulb")
    bulb += idiot
    bulb.save()
    fire(Create, ref=idiot)

    ev_handler = EventHandler("Event")
    ev_handler.start()
```

For a more elaborate mongorm event-driven system check out EventSubscriber.py in examples.
