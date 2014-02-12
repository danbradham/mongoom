.. _api:

Interface Essentials
====================

One function and five classes, all you need to use Mongoom.

Connection
----------

.. module:: mongoom.connection

.. autofunction:: mongoom.connection.connect

Documents
---------

.. module:: mongoom.documents

.. autoclass:: mongoom.documents.Document
    :members:

.. autoclass:: mongoom.documents.EmbeddedDocument
    :members:

Fields
------

.. module:: mongoom.fields

.. autoclass:: mongoom.fields.Field
.. autoclass:: mongoom.fields.ListField
.. autoclass:: mongoom.fields.ObjectIdField

Document Based Events
=====================

.. module:: mongoom.events

Insert Event objects into a capped collection using fire.

.. autoclass:: mongoom.events.Event

Subscribers
===========

.. module:: mongoom.subscriber

Subscribe to a capped collection using a Subscriber.

.. autoclass:: mongoom.subscriber.Subscriber
    :members:
