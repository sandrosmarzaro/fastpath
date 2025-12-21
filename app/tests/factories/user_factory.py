from factory.base import Factory
from factory.declarations import LazyAttribute, Sequence

from app.models.user_model import UserModel


class UserFactory(Factory):
    class Meta:
        model = UserModel

    username = Sequence(lambda n: f'test{n}')
    email = LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = LazyAttribute(lambda obj: f'{obj.username}')
