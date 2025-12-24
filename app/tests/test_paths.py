from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from uuid6 import uuid7

from app.models.path_model import PathModel
from app.schemas.path_schema import PathResponse


class TestPaths:
    BASE_URI = '/api/v1/paths'

    @pytest.mark.usefixtures('osrm_response')
    def test_create_path_sucessful(
        self,
        client: TestClient,
        access_token: str,
        path_request: dict,
    ) -> None:
        response = client.post(
            self.BASE_URI,
            headers={'Authorization': f'Bearer {access_token}'},
            json=path_request,
        )
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
        access_token: str,
        wrong_path_request: dict,
    ) -> None:
        response = client.post(
            self.BASE_URI,
            headers={'Authorization': f'Bearer {access_token}'},
            json=wrong_path_request,
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_paths_should_return_empty(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.get(
            self.BASE_URI,
            headers={'Authorization': f'Bearer {access_token}'},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'data': []}

    def test_get_paths_should_return_one(
        self,
        client: TestClient,
        access_token: str,
        path: PathModel,
    ) -> None:
        response = client.get(
            self.BASE_URI,
            headers={'Authorization': f'Bearer {access_token}'},
        )
        path_schema = PathResponse.model_validate(path).model_dump(mode='json')

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'data': [path_schema]}

    def test_get_one_path_sucessful(
        self, client: TestClient, path: PathModel, access_token: str
    ) -> None:
        response = client.get(
            f'{self.BASE_URI}/{path.id}',
            headers={'Authorization': f'Bearer {access_token}'},
        )
        path_schema = PathResponse.model_validate(path).model_dump(mode='json')

        assert response.status_code == HTTPStatus.OK
        assert response.json() == path_schema

    def test_get_one_path_should_return_not_found(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.get(
            f'{self.BASE_URI}/{uuid7()}',
            headers={'Authorization': f'Bearer {access_token}'},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_should_delete_path_sucessful(
        self, client: TestClient, path: PathModel, access_token: str
    ) -> None:
        response = client.delete(
            f'{self.BASE_URI}/{path.id}',
            headers={'Authorization': f'Bearer {access_token}'},
        )

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.content == b''

    def test_should_return_not_found_when_delete_no_existis_path(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.delete(
            f'{self.BASE_URI}/{uuid7()}',
            headers={'Authorization': f'Bearer {access_token}'},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_should_error_when_get_path_of_other_user(
        self,
        client: TestClient,
        access_tokens: tuple[str, str],
        paths: tuple[PathModel, PathModel],
    ) -> None:
        first_path, _ = paths
        _, second_token = access_tokens
        response = client.get(
            f'{self.BASE_URI}/{first_path.id}',
            headers={'Authorization': f'Bearer {second_token}'},
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_should_error_when_delete_path_of_other_user(
        self,
        client: TestClient,
        access_tokens: tuple[str, str],
        paths: tuple[PathModel, PathModel],
    ) -> None:
        first_path, _ = paths
        _, second_token = access_tokens
        response = client.delete(
            f'{self.BASE_URI}/{first_path.id}',
            headers={'Authorization': f'Bearer {second_token}'},
        )

        assert response.status_code == HTTPStatus.FORBIDDEN
