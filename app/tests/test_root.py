from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from app.schemas.health_check_schema import HealthCheckResponse


class TestRoot:
    def test_redirect_root_to_swagger(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.get(
            '/', headers={'Authorization': f'Bearer {access_token}'}
        )
        assert response.status_code == HTTPStatus.OK
        assert response.history[0].status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert '/docs' in str(response.url)
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

    @pytest.mark.usefixtures('prod_settings')
    def test_redirect_root_to_health_route(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.get(
            '/', headers={'Authorization': f'Bearer {access_token}'}
        )
        assert response.status_code == HTTPStatus.OK
        assert response.history[0].status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert '/api' in str(response.url)
        assert response.headers['Content-Type'] == 'application/json'
        assert HealthCheckResponse(**response.json()) == HealthCheckResponse()
