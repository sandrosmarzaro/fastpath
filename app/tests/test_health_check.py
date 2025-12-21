from http import HTTPStatus

from fastapi.testclient import TestClient

from app.schemas.health_check_schema import HealthCheckResponse


class TestHealthCheck:
    def test_health_check_should_return_200(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.get(
            '/api/v1/', headers={'Authorization': f'Bearer {access_token}'}
        )
        assert response.status_code == HTTPStatus.OK

    def test_health_check_response_should_is_json(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.get(
            '/api/v1/', headers={'Authorization': f'Bearer {access_token}'}
        )
        assert response.headers['Content-Type'] == 'application/json'

    def test_health_check_should_response_status_ok(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.get(
            '/api/v1/', headers={'Authorization': f'Bearer {access_token}'}
        )
        assert HealthCheckResponse(**response.json()) == HealthCheckResponse()
