Welcome to Serializer documentation!
==================================

Serializer provides Easy object serialization. Mimics RoR ActiveRecord serializer.


QuickStart
==========

1. Make your class inherit Serializable mixin.
2. Define attributes() method and make it return a list of property names

Example::

    from serializer import Serializable


    class User(Serializable):
        first_name = 'John'
        last_name = 'Matrix'
        email = 'john.matrix@example.com'
        protected_property = 'this value is not included in json'

        def attributes(self):
            return ['first_name', 'last_name', 'email']

    user = User()
    user.as_json()
    # "{'first_name': 'John', 'last_name': 'Matrix'}"

    user.as_json_dict()
    # {'first_name': 'John', 'last_name': 'Matrix'}


How to handle relations
=======================

Serializer supports serializing of deep object structures. Let's say we have two classes
Event and Location and we want to jsonify an event along with its location. ::


    class Location(Serializable):
        name = 'Some Location'

        def attributes(self):
            return ['name']

    class Event(Serializable):
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


Using attribute sets
====================

Many times you may have situations where having one default attribute list is not
enough. For example you may have multiple views that return user details and many views
that return user with only its basic info. ::

    class User(Serializable):
        first_name = 'John'
        last_name = 'Matrix'
        email = 'john.matrix@example.com'
        age = 33
        is_active = True

        def attributes(self):
            return ['first_name', 'last_name', 'email']

        def attribute_sets(self):
            return {'details': ['age', 'is_active']}


    user = User()
    user.as_json_dict(include='details')
    '''
        {
            'first_name': 'John',
            'last_name': 'Matrix',
            'email': 'john.matrix@example.com',
            'age': 33,
            'is_active': True
        }
    '''


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

