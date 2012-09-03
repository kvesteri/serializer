Welcome to bourne documentation!
==================================

Bourne provides smart Python object to json conversion.


QuickStart
==========

Example::

    from bourne import BourneMixin


    class User(BourneMixin):
        first_name = 'John'
        last_name = 'Matrix'
        email = 'john.matrix@example.com'
        protected_property = 'this value is not included in json'

        def attributes(self):
            return ['first_name', 'last_name', 'email']

    user = User()
    user.as_json()
    # "{'first_name': 'John', 'last_name': 'Matrix'}"


How to handle relations
=======================

Let's say we have two classes Event and Location and we want to jsonify an
event along with its location.::

    class Location(BourneMixin):
        name = 'Some Location'

        def attributes(self):
            return ['name']

    class Event(BourneMixin):
        name = 'Some Event'
        location = Location()

        def attributes(self):
            return ['name', 'location']


    event = Event()
    event.as_json()
    # "{'name': 'Some Event', 'location': {'name': 'Some Location'}}"


Using exclude, include and only
===============================

You can fine-grain what gets included in json format by using exclude, include
and only parameters. ::

    User.as_json(only=['name', 'email'])  # include only name and email

    # include all the fields defined in attributes as well as age
    User.as_json(include=['age'])

    # include all the field defined in attributes but exclude 'email'
    User.as_json(include=['email'])


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

