.. _api:

Essentials
==========

One function and five classes represent all you need to use Mongoom.

.. autofunction:: mongoom.connection.connect
.. autoclass:: mongoom.documents.Document
.. autoclass:: mongoom.documents.EmbeddedDocument
.. autoclass:: mongoom.fields.Field
.. autoclass:: mongoom.fields.ListField
.. autoclass:: mongoom.fields.ObjectId

Document Based Events
=====================

Insert Event objects into a capped collection using fire.

.. autoclass:: mongoom.events.Event
.. autofunction:: mongoom.events.fire

Subscribers
===========

Subscribe to a capped collection using a Subscriber.

.. autoclass:: mongoom.subscriber.Subscriber
