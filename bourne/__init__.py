import simplejson as json


class Empty():
    pass


empty = Empty()


def is_callable(object):
    _type = type(object).__name__
    return _type == 'instancemethod' or _type == 'function'


def dumps(value, args):
    if is_callable(value):
        value = value()
    value = dump_object(value, args)
    return value


class BourneMixin(object):
    def attributes(self):
        """
        This method is being used by as_json for defining the default json
        attributes for this model.

        Models using JSONMixin can override this and return a list of desired
        default attributes.
        """
        return self.__table__.c.keys()

    def attribute_sets(self):
        """
        This method should return a dict with keys as attribute set names and
        values as desired attribute sets

        Attribute sets can be used as a convenient shortcuts in as_json()

        Examples::

            >>> User(JSONMixin):
            ...     def attribute_sets():
            ...         return {'details': ['id', 'name', 'age']}
            >>> User(id=1, name='someone',).as_json(only='details')
            {'id': 1, 'name': 'Someone', 'age': 14}
        """
        return {}

    def as_json(self, only=None, exclude=None, include=None):
        """
        This mimics the as_json found in RoR ActiveModel
        for more info see:
        http://api.rubyonrails.org/classes/ActiveModel/Serializers/JSON.html
        """
        return json.dumps(self.as_json_dict(), use_decimal=True)

    def as_json_dict(self, only=None, exclude=None, include=None):
        """
        Returns object attributes as a dictionary with jsonified values

        Without any options, the returned JSON string will include all the
        fields returned by the models attribute() method. For example:

        user = User.query.get(1)
        user.as_json()

        # => {"id": 1,
              "name": "John Matrix",
              "first_name": "John",
              "last_name": "Matrix"}

        The 'only' and 'exclude' options can be used to limit the attributes
        included. For example:

        user.as_json(only=['id', 'name'])
        # => {"id": 1, "name": "John Matrix"}

        user.as_json(exclude=['id'])
        # => {"name": "John Matrix",
              "first_name": "John",
              "last_name": "Matrix"}

        To include the result of some additional attributes, method calls,
        attribute sets or associations on the model use 'include'.

        user.as_json(include=['weight'])
        # => {"id": 1,
              "name": "John Matrix",
              "first_name": "John",
              "last_name": "Matrix",
              "weight": 100}

        In order to fine grain what gets included in associations you can use
        'include' parameter with additional arguments.

        user.as_json(include=[('posts', {'include': 'details'})]
        # => {"id": 1,
              "name": "John Matrix",
              "first_name": "John",
              "last_name": "Matrix",
              "weight": 100,
              "posts": [
                  {"id": 1, "author_id": 1, "title": "First post"},
                  {"id": 2, author_id: 1, "title": "Second post"}
              ]}

        Second level and higher order associations work as well:

        user.as_json('include'= [('posts',
              {
              'include': [
                      ('comments, {'only': ['body']})
                  ],
              'only': [title]
              }
        )]

        # => {"id": 1,
              "name": "John Matrix",
              "first_name": "John",
              "last_name": "Matrix",
              "weight": 100,
              "posts": [
                  {"comments": [{"body": "1st post!"}, {"body": "Second!"}],
                  "title": "Welcome to the weblog"},
                  {"comments": [{"body": "Don't think too hard"}],
                  "title": "So I was thinking"}
              ]}
        """
        return jsonify_model(self, only=only, exclude=exclude, include=include)


def jsonify_model(model, only=None, exclude=None, include=None):
    """
    Jsonifies given model object

    See :func:`as_json` for more info

    :param model: object to be converted into json
    :param only: list of attributes to be included in json, if this parameter
        is not set attributes() method of the model will be used for obtaining
        the list of attributes names
    :param exclude: list of attributes to be excluded from the json format
    :param include: list of attribute names to be included in json, attribute
        names can be any properties of `model` (even method names)
    """
    json = {}
    if only:
        json.update(jsonify_iterable(model, only))
    else:
        json.update(jsonify_iterable(model, model.attributes(), exclude))
    if include:
        json.update(jsonify_iterable(model, include))

    return cleanup(json)


OBJECT_DUMPERS = {
    BourneMixin: lambda a, b: jsonify_model(a, **copy_args(b)),
    'datetime': lambda a, b: a.isoformat() + 'Z' if a else None,
    'date': lambda a, b: a.isoformat() if a else None,
    'list': lambda a, b: [dumps(c, b) for c in a],
}


def register_dumper(key, dumper_callable):
    """
    Registers new dumper for given class type

    Examples::
        >>> class MyClassA(object):
        ...     pass
        >>> class MyClassB(MyClassA):
        ...     pass
        >>> register_dumper('MyClassA', lambda a: 'myclass')
        >>> dump_object(MyClassA())
        "myclass"
        >>> dump_object(MyClassB())
        <MyClassB instance>


        >>> class MyClassA(object):
        ...     pass
        >>> class MyClassB(MyClassA):
        ...     pass
        >>> register_dumper(MyClassA, lambda a: 'myclass')
        >>> dump_object(MyClassA())
        "myclass"
        >>> dump_object(MyClassB())
        "myclass"
    """
    OBJECT_DUMPERS[key] = dumper_callable


def dump_object(value, args):
    """
    Serializes a non callable variable

    Examples::
        >>> dump_object(datetime(2000, 11, 11))
        "2000-11-11 00:00:00Z"
    """
    #print value, args
    for class_ in OBJECT_DUMPERS:
        if isinstance(class_, basestring):
            if class_ == value.__class__.__name__:
                value = OBJECT_DUMPERS[class_](value, args)
        elif isinstance(value, class_):
            value = OBJECT_DUMPERS[class_](value, args)
    return value


def copy_args(args):
    copy_args = {}
    if 'only' in args:
        copy_args['only'] = args['only']
    if 'include' in args:
        copy_args['include'] = args['include']
    if 'exclude' in args:
        copy_args['exclude'] = args['exclude']
    return copy_args


def unpack_args(args):
    """
    unpacks args

    Used by jsonifiers
    """
    if isinstance(args, tuple):
        return args
    else:
        return (args, {})


def unpack_key(key):
    """
    Unpacks given key

    For example the unpacked format of key "key as key1" is
    {
        'name': 'key',
        'alias': 'key1'
    }
    """
    parts = key.split(' as ')
    if len(parts) == 1:
        parts.append(parts[0])
    return parts


def cleanup(json):
    """
    Remove all missing values. Sometimes its useful for object methods
    to return missing value in order to not include that value in the
    json format.

    Examples::

        >>> User(JSONMixin):
        ...     def attributes():
        ...         return ['id', 'name', 'birthday', 'somefunc']
        ...     def age():
        ...         if birthday:
        ...             return empty
        ...         else:
        ...             return calc_age(self.birthday)


    Now if some user has birthday the age function is going to return the age.
    However if user doesn't have birthday the age function is returning a
    special empty value which tells jsonifier not to include that key in
    json format.

        >>> User(id=1, name='someone').as_json()
        {'id': 1, 'name': 'Someone'}
    """
    return dict(filter(lambda a: a[1] is not empty, json.items()))


def jsonify_iterable(model, iterable, exclude=None):
    """
    Jsonifies iterable

    :param model: model of which the attributes belong to
    :param iterable: attributes as iterable
    :param exclude: excluded attributes
    """
    attr_sets = model.attribute_sets()
    json = {}

    for json_key, args in map(unpack_args, iterable):
        if exclude and json_key in exclude:
            continue
        if json_key in attr_sets:
            subattrs = attr_sets[json_key]
            for key, subargs in map(unpack_args, subattrs):
                model_attr, alias = unpack_key(key)
                json[alias] = jsonify_attribute(model, model_attr, subargs)
        else:
            model_attr, alias = unpack_key(json_key)
            json[alias] = jsonify_attribute(model, model_attr, args)
    return json


def jsonify_attribute(model, attr, args=None):
    """
    Jsonifies single object attribute

    :param model: model of which the attribute belongs to
    :param attr: the name of the attribute
    :param args: additional args
    """
    if not args:
        args = {}

    if not hasattr(model, attr):
        value = empty
    else:
        value = getattr(model, attr)

    value = dumps(value, args)

    return value
