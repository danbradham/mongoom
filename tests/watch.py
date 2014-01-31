from pymongo import Connection
import time

db = Connection().my_db
coll = db.my_collection
cursor = coll.find(tailable=True)
while cursor.alive:
    try:
        doc = cursor.next()
    except StopIteration:
        if doc:
            print doc
            doc = None
        time.sleep(1)
