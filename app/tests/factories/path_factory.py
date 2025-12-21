from factory.base import Factory
from factory.declarations import List, SubFactory
from factory.faker import Faker

from app.models.path_model import PathModel
from app.tests.factories.coordinates_factory import (
    CoordinatesFactory,
    CoordinatesRequestFactory,
)


class PathRequestFactory(Factory):
    class Meta:
        model = dict

    pickup = SubFactory(CoordinatesRequestFactory)
    dropoff = List([SubFactory(CoordinatesRequestFactory) for _ in range(5)])


class PathFactory(Factory):
    class Meta:
        model = PathModel

    user_id = Faker('uuid4')
    pickup = SubFactory(CoordinatesFactory)
    dropoff = List([SubFactory(CoordinatesFactory) for _ in range(5)])
