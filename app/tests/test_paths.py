from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from respx import Route


class TestPaths:
    BASE_URI = '/api/v1/paths'

    def test_create_path_sucessfull(
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
