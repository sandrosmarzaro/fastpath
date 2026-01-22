from factory.base import Factory
from factory.faker import Faker

from app.models.user_model import UserModel


class UserFactory(Factory):
    class Meta:
        model = UserModel

    username = Faker('user_name')
    email = Faker('email')
    password = Faker('password')
