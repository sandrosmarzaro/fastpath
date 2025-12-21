from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.models.user_model import UserModel


class TestAuth:
    BASE_URI = '/api/v1/auth'
    INITIAL_TIME = '2025-12-31 23:00:00'
    EXPIRED_TIME = '2026-01-01 00:00:00'

    def test_create_access_token_sucessful(
        self, client: TestClient, user: UserModel
    ) -> None:
        response = client.post(
            f'{self.BASE_URI}/token',
            data={
                'username': user.username,
                'password': user.clean_password,  # type: ignore[attr-defined]
            },
        )
        token = response.json()

        assert response.status_code == HTTPStatus.OK
        assert 'access_token' in token
        assert token['token_type'] == 'Bearer'  # noqa: S105

    def test_raise_error_when_create_token_with_wrong_username(
        self, client: TestClient, user: UserModel
    ) -> None:
        response = client.post(
            f'{self.BASE_URI}/token',
            data={
                'username': 'wrong_username',
                'password': user.clean_password,  # type: ignore[attr-defined]
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            'error': 'UnauthorizedError',
            'detail': 'username or password doesnt match',
        }

    def test_raise_error_when_create_token_with_wrong_password(
        self, client: TestClient, user: UserModel
    ) -> None:
        response = client.post(
            f'{self.BASE_URI}/token',
            data={
                'username': user.username,
                'password': 'wrong_password',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            'error': 'UnauthorizedError',
            'detail': 'username or password doesnt match',
        }

    def test_raise_error_when_token_expired(
        self, client: TestClient, user: UserModel
    ) -> None:
        with freeze_time(self.INITIAL_TIME):
            response = client.post(
                f'{self.BASE_URI}/token',
                data={
                    'username': user.username,
                    'password': user.clean_password,  # type: ignore[attr-defined]
                },
            )
            token = response.json()

            assert response.status_code == HTTPStatus.OK
            assert 'access_token' in token
            assert token['token_type'] == 'Bearer'  # noqa: S105

        with freeze_time(self.EXPIRED_TIME):
            response = client.get(
                '/api/v1',
                headers={'Authorization': f'Bearer {token}'},
            )

            assert response.status_code == HTTPStatus.UNAUTHORIZED
            assert response.json() == {
                'error': 'UnauthorizedError',
                'detail': 'could not validate credentials',
            }

    def test_create_refresh_token_sucessful(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.post(
            f'{self.BASE_URI}/refresh_token',
            headers={'Authorization': f'Bearer {access_token}'},
        )
        token = response.json()

        assert response.status_code == HTTPStatus.OK
        assert 'access_token' in token
        assert token['token_type'] == 'Bearer'  # noqa: S105

    def test_raise_error_when_refresh_token_expired(
        self, client: TestClient, user: UserModel
    ) -> None:
        with freeze_time(self.INITIAL_TIME):
            response = client.post(
                f'{self.BASE_URI}/token',
                data={
                    'username': user.username,
                    'password': user.clean_password,  # type: ignore[attr-defined]
                },
            )
            token = response.json()

            assert response.status_code == HTTPStatus.OK
            assert 'access_token' in token
            assert token['token_type'] == 'Bearer'  # noqa: S105

        with freeze_time(self.EXPIRED_TIME):
            response = client.post(
                f'{self.BASE_URI}/refresh_token',
                headers={'Authorization': f'Bearer {token}'},
            )

            assert response.status_code == HTTPStatus.UNAUTHORIZED
            assert response.json() == {
                'error': 'UnauthorizedError',
                'detail': 'could not validate credentials',
            }
