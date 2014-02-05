from pymongorm import (connect, EmbeddedDocument, Document, Field,
                       ListField, get_connection)


class User(Document):
    _index = {"key_or_list": [("name", 1), ("last_name", 1)], "unique": True}
    name = Field(basestring, required=True)
    last_name = Field(basestring, required=True)


class Component(Document):
    _index = {"key_or_list": [("name", 1), ("created", 1)], "unique": True}
    name = Field(basestring)
    user = Field(User)
    components = ListField(Document)


class CheckListItem(EmbeddedDocument):
    text = Field(basestring)
    checked = Field(bool, default=False)


class CheckList(Document):
    title = Field(basestring)
    user = Field(User)
    items = ListField(CheckListItem)


def test_ref():

    user_a = User(name="User", last_name="A").save()
    comp_a = Component(name="Component A", user=user_a).save()
    comp_b = Component(name="Component B", user=user_a).save()
    comp_a.components += comp_b
    comp_a.save()
    pprint(comp_a.data)


def test_embed():

    user_a = User.find_one(name="User", last_name="A")
    clist = CheckList(title="New Checklist", user=user_a).save()
    clist_item_a = CheckListItem(text="Item A")

    clist.items += clist_item_a
    clist.save()

    pprint(clist.data)
    clist_item_a.text = "Item A Changed"
    print type(clist_item_a)
    pprint(clist.data)
    print type(clist.items[0])
    clist.items[0].text = "Item A Changed Twice"
    pprint(clist.data)


if __name__ == '__main__':
    from pprint import pprint
    connect("test_db")
    c = get_connection()
    c.drop_database("test_db")

    test_ref()
    test_embed()
