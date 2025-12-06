from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from respx import Route
from uuid6 import uuid6

from app.models.path_model import PathModel
from app.schemas.path_schema import PathResponse


class TestPaths:
    BASE_URI = '/api/v1/paths'

    def test_create_path_sucessful(
        self,
        client: TestClient,
        path_request: dict,
        osrm_response: Route,  # noqa: ARG002
    ) -> None:
        response = client.post(self.BASE_URI, json=path_request)
        data = response.json()

        assert response.status_code == HTTPStatus.CREATED
        assert data['pickup']['lat'] == pytest.approx(
            path_request['pickup']['lat'],
        )
        assert data['pickup']['lng'] == pytest.approx(
            path_request['pickup']['lng'],
        )
        assert len(data['dropoff']) == len(path_request['dropoff'])

    def test_create_bad_format_path(
        self,
        client: TestClient,
        wrong_path_request: dict,
    ) -> None:
        response = client.post(self.BASE_URI, json=wrong_path_request)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_paths_should_return_empty(self, client: TestClient) -> None:
        response = client.get(self.BASE_URI)

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'data': []}

    def test_get_paths_should_return_one(
        self,
        client: TestClient,
        path: PathModel,
    ) -> None:
        response = client.get(self.BASE_URI)
        path_schema = PathResponse.model_validate(path).model_dump(mode='json')

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'data': [path_schema]}

    def test_get_one_path_sucessful(
        self, client: TestClient, path: PathModel
    ) -> None:
        response = client.get(f'{self.BASE_URI}/{path.id}')
        path_schema = PathResponse.model_validate(path).model_dump(mode='json')

        assert response.status_code == HTTPStatus.OK
        assert response.json() == path_schema

    def test_get_one_path_should_return_not_found(
        self, client: TestClient
    ) -> None:
        response = client.get(f'{self.BASE_URI}/{uuid6()}')

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_should_delete_path_sucessful(
        self, client: TestClient, path: PathModel
    ) -> None:
        response = client.delete(f'{self.BASE_URI}/{path.id}')

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.content == b''

    def test_should_return_not_found_when_delete_no_existis_path(
        self, client: TestClient
    ) -> None:
        response = client.delete(f'{self.BASE_URI}/{uuid6()}')

        assert response.status_code == HTTPStatus.NOT_FOUND
