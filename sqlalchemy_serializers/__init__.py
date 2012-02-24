from copy import copy
from datetime import datetime, date
from sqlalchemy.types import Enum


class Empty():
    pass


empty = Empty()


def is_callable(object):
    _type = type(object).__name__
    return _type == 'instancemethod' or _type == 'function'


def dumps(value, args=None):
    if not args:
        args = {}

    value = dump_callable(value, args)
    value = dump_non_callable(value, args)

    if 'default' in args and value is None:
        default = args['default']
        value = dumps(default, copy_args(args))
    return value


def dump_callable(value, args):
    if is_callable(value):
        func_args = []
        if 'func_args' in args:
            func_args = args['func_args']

        if isinstance(func_args, list):
            value = value(*func_args)
        elif isinstance(func_args, dict):
            value = value(**func_args)
        else:
            value = value(func_args)
    return value


def dump_non_callable(value, args):
    """
    Serializes a non callable variable

    Examples::
        >>> dump_non_callable(datetime(2000, 11, 11))
        "2000-11-11 00:00:00Z"
    """
    if isinstance(value, JSONMixin):
        value = jsonify_model(value, **copy_args(args))
    elif isinstance(value, list):
        tmp = []
        for obj in value:
            tmp.append(dumps(obj, args))
        return tmp
    elif isinstance(value, datetime):
        value = value.isoformat() + 'Z' if value else None
    elif isinstance(value, date):
        value = value.isoformat() if value else None
    elif isinstance(value, Enum):
        value = None
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


class JSONMixin(object):
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
            >>> User(Model, JSONMixin):
                def attribute_sets():
                    return {'details': ['id', 'name', 'age']}

            >>> User.as_json(only='details')

            {'id': 1, 'name': 'Someone', 'age': 14}
        """
        return {}

    def as_json(self, only=None, exclude=None, include=None):
        """
        This mimics the as_json found in RoR ActiveModel
        for more info see:
        http://api.rubyonrails.org/classes/ActiveModel/Serializers/JSON.html

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


def unpack_args(args):
    """
    unpacks args

    Used by jsonifiers
    """
    if isinstance(args, tuple):
        return args
    else:
        return (args, {})


def cleanup(json):
    """
    Remove all missing values. Sometimes its useful for object methods
    to return missing value in order to not include that value in the
    json format.
    """
    for key in copy(json):
        if json[key] is empty:
            del json[key]
    return json


def jsonify_model(model, only=None, exclude=None, include=None):
    """
    Jsonifies given model object

    See :func:`as_json` for more info
    """
    json = {}
    if only:
        json.update(jsonify_iterable(model, only))
    else:
        json.update(jsonify_iterable(model, model.attributes(), exclude))
    if include:
        json.update(jsonify_iterable(model, include))

    return cleanup(json)


def jsonify_iterable(model, iterable, exclude=None):
    attr_sets = model.attribute_sets()
    json = {}

    for json_key, args in map(unpack_args, iterable):
        if exclude and json_key in exclude:
            continue
        if json_key in attr_sets:
            subattrs = attr_sets[json_key]
            for key, subargs in map(unpack_args, subattrs):
                json[key] = jsonify_attribute(model, key, subargs)
        else:
            json[json_key] = jsonify_attribute(model, json_key, args)
    return json


def jsonify_attribute(model, json_key, args=None):
    if not args:
        args = {}
    if 'attr' not in args:
        args['attr'] = json_key

    if type(args['attr']).__name__ == 'function':
        value = args['attr']
    else:
        if not hasattr(model, args['attr']):
            value = empty
        else:
            value = getattr(model, args['attr'])

    value = dumps(value, args)

    return value
