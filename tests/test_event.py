from pymongorm import connect, fire, Event, Document, Field, get_connection

connect("test_db")
c = get_connection()
c.drop_database("test_db")

class User(Document):
    name = Field(basestring, required=True)
    last_name = Field(basestring, required=True)

frank = User(name="Frank", last_name="Footer").save()


def test_fire():

    fire(Event, ref=frank)


def test_custom_event():

    class Updated(Event):
        '''Custom update event'''

    frank.last_name = "Footers"
    fire(Updated, ref=frank.save(), user=frank)
