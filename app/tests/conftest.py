from collections.abc import AsyncGenerator, Generator
from http import HTTPStatus
from typing import Any

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import Response
from respx import MockRouter, Route
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from app.core.database import get_session
from app.core.settings import settings
from app.main import app
from app.models.path_model import PathModel
from app.models.table_model import TableModel
from app.tests.factories.coordinates_factory import (
    CoordinatesRequestFactory,
)
from app.tests.factories.path_factory import PathFactory, PathRequestFactory


@pytest.fixture(scope='session')
def engine() -> Generator[AsyncEngine]:
    with PostgresContainer('postgres:18-alpine', driver='psycopg') as postgres:
        yield create_async_engine(postgres.get_connection_url())


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, Any]:
    async with engine.begin() as conn:
        await conn.run_sync(TableModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(TableModel.metadata.drop_all)


@pytest.fixture
def client(session: AsyncSession) -> Generator[TestClient]:
    def get_session_overdrive() -> AsyncSession:
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_overdrive
        yield client
        app.dependency_overrides.clear()


@pytest.fixture
def path_request() -> dict:
    return PathRequestFactory.build()


@pytest.fixture
def wrong_path_request() -> dict:
    return PathRequestFactory.build(
        pickup=CoordinatesRequestFactory(lat='invalid')
    )


@pytest.fixture
def osrm_response(respx_mock: MockRouter) -> Route:
    response = {
        'code': 'Ok',
        'durations': [
            [0, 189.4, 59.5, 177.5, 40.5, 171.4],
            [262.8, 0, 200.4, 318.4, 303.3, 312.3],
            [62.4, 190, 0, 118, 102.9, 111.9],
            [131.5, 320.9, 191, 0, 172, 181],
            [158.6, 213.8, 96.2, 214.2, 0, 208.1],
            [61.8, 251.2, 121.3, 130.6, 102.3, 0],
        ],
        'distances': [
            [0, 1668.7, 970.9, 2093.5, 281, 2452.6],
            [2556.4, 0, 1635.4, 2758, 2837.4, 3117.2],
            [921, 1333.7, 0, 1122.5, 1202, 1481.7],
            [1024.1, 2692.8, 1995, 0, 1305.1, 1584.8],
            [1821.1, 1378.7, 900.1, 2022.6, 0, 2381.8],
            [914.7, 2583.4, 1885.7, 1306.5, 1195.8, 0],
        ],
    }
    return respx_mock.get(url__startswith=settings.OSRM_URL).mock(
        return_value=Response(HTTPStatus.OK, json=response)
    )


@pytest_asyncio.fixture
async def path(session: AsyncSession) -> PathModel:
    new_path = PathFactory()
    session.add(new_path)
    await session.commit()
    await session.refresh(new_path)
    return new_path
