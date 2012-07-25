from datetime import datetime, date
from json_alchemy import JSONAlchemyMixin, empty


class TeamQuery(object):
    def get(self, id):
        team = Team()
        team.id = id
        team.name = 'some team'


class Team(JSONAlchemyMixin):
    __tablename__ = 'team'

    query = TeamQuery()

    def attributes(self):
        return ['name']


class User(JSONAlchemyMixin):
    __tablename = 'user'

    def attributes(self):
        return [
            'name',
            'age',
            'created_at'
        ]

    def somemethod(self):
        return 123


class TestDumpTypes(object):
    def setup_method(self, method):
        pass

    def test_supports_datetime_type(self):
        user = User()
        user.name = 'John Matrix'
        user.age = 21
        user.created_at = datetime(2011, 1, 1)

        json = {
            'created_at': '2011-01-01T00:00:00Z',
            'age': 21,
            'name': 'John Matrix'
        }

        assert user.as_json() == json

    def test_supports_instance_methods(self):
        user = User()
        json = {
            'somemethod': 123
        }
        assert user.as_json(only=['somemethod']) == json

    def test_supports_date_type(self):
        user = User()
        user.name = 'John Matrix'
        user.age = 21
        user.created_at = date(2011, 1, 1)

        json = {
            'created_at': '2011-01-01',
            'age': 21,
            'name': 'John Matrix'
        }

        assert user.as_json() == json

    def test_supports_list_type(self):
        user = User()
        user.name = 'John Matrix'
        user.friends = [1, 2, 3, 4]
        user.age = None
        user.created_at = None

        json = {
            'created_at': None,
            'age': None,
            'name': 'John Matrix',
            'friends': [1, 2, 3, 4]
        }
        assert user.as_json(include=['friends']) == json

    def test_supports_lists_with_datetimes(self):
        user = User()
        user.dates = [datetime(2011, 1, 1)]

        json = {
            'dates': ['2011-01-01T00:00:00Z']
        }
        assert user.as_json(only=['dates']) == json


class TestSerializationParams(object):
    def setup_method(self, method):
        pass

    def test_supports_aliases(self):
        user = User()
        user.name = 'John Matrix'
        user.age = None
        user.created_at = None

        json = {
            'fullname': 'John Matrix'
        }

        assert user.as_json(only=[('name as fullname')]) == json

    def test_supports_exclude(self):
        user = User()
        user.name = 'John Matrix'

        json = {
            'name': 'John Matrix'
        }

        assert user.as_json(exclude=['age', 'created_at']) == json

    def test_none_can_be_used_as_default_argument(self):
        user = User()
        user.name = None

        json = {
            'name': None
        }

        assert user.as_json(only=[('name', {'default': None})]) == json

    def test_supports_object_nesting(self):
        userA = User()
        userA.name = 'John'
        userB = User()
        userB.name = 'Jack'
        userA.friend = userB

        json = {'name': 'John', 'friend': {'name': 'Jack'}}

        assert userA.as_json(only=[
            'name',
            ('friend', {'only': ['name']})
        ]) == json

    def test_accepts_aliases_for_related_objects(self):
        userA = User()
        userA.name = 'John'
        userB = User()
        userB.name = 'Jack'
        userA.friend = userB

        json = {'name': 'John', 'friend 1': {'name': 'Jack'}}

        assert userA.as_json(only=[
            'name',
            ('friend as friend 1', {'only': ['name']})
        ]) == json

    def test_supports_json_cleanup(self):
        user = User()
        user.name = empty

        user.as_json(only=['name']) == {}
