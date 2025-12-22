from http import HTTPStatus

from fastapi.testclient import TestClient
from uuid6 import uuid7

from app.models.user_model import UserModel
from app.schemas.user_schema import UserResponse


class TestUsers:
    BASE_URI = '/api/v1/users'

    def test_create_user_successful(self, client: TestClient) -> None:
        body_request = {
            'username': 'username',
            'email': 'email@example.com',
            'password': 'password',
        }
        response = client.post(
            self.BASE_URI,
            json=body_request,
        )
        data = response.json()

        assert response.status_code == HTTPStatus.CREATED
        assert 'id' in data
        assert data['username'] == body_request['username']
        assert data['email'] == body_request['email']

    def test_create_user_with_same_username_failure(
        self, client: TestClient, user: UserModel
    ) -> None:
        response = client.post(
            self.BASE_URI,
            json={
                'username': user.username,
                'email': 'email@example.com',
                'password': 'password',
            },
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {
            'error': 'ConflictError',
            'detail': 'username already in use.',
        }

    def test_create_user_with_same_email_failure(
        self, client: TestClient, user: UserModel
    ) -> None:
        response = client.post(
            self.BASE_URI,
            json={
                'username': 'username',
                'email': user.email,
                'password': 'password',
            },
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {
            'error': 'ConflictError',
            'detail': 'email already in use.',
        }

    def test_get_one_user_successful(
        self, client: TestClient, user: UserModel, access_token: str
    ) -> None:
        response = client.get(
            f'{self.BASE_URI}/{user.id}',
            headers={'Authorization': f'Bearer {access_token}'},
        )

        user_schema = UserResponse.model_validate(user).model_dump(mode='json')
        assert response.status_code == HTTPStatus.OK
        assert response.json() == user_schema

    def test_get_other_user_failure(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.get(
            f'{self.BASE_URI}/{uuid7()}',
            headers={
                'Authorization': f'Bearer {access_token}',
            },
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_update_all_user_fields_successful(
        self, client: TestClient, user: UserModel, access_token: str
    ) -> None:
        body_request = {
            'username': 'username',
            'email': 'email@example.com',
            'password': 'password',
        }
        response = client.put(
            f'{self.BASE_URI}/{user.id}',
            headers={'Authorization': f'Bearer {access_token}'},
            json=body_request,
        )

        data = response.json()
        assert response.status_code == HTTPStatus.OK
        assert data['id'] == str(user.id)
        assert data['username'] == body_request['username']
        assert data['email'] == body_request['email']

    def test_update_other_user_failure(
        self, client: TestClient, access_token: str
    ) -> None:
        body_request = {
            'username': 'username',
            'email': 'email@example.com',
            'password': 'password',
        }
        response = client.put(
            f'{self.BASE_URI}/{uuid7()}',
            headers={'Authorization': f'Bearer {access_token}'},
            json=body_request,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_update_user_with_same_username_failure(
        self,
        client: TestClient,
        users: tuple[UserModel, UserModel],
        access_tokens: tuple[str, str],
    ) -> None:
        first_user, second_user = users
        first_token, _ = access_tokens
        response = client.put(
            f'{self.BASE_URI}/{first_user.id}',
            headers={'Authorization': f'Bearer {first_token}'},
            json={
                'username': second_user.username,
                'email': 'email@example.com',
                'password': 'password',
            },
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {
            'error': 'ConflictError',
            'detail': 'username or email already in use.',
        }

    def test_update_user_with_same_email_failure(
        self,
        client: TestClient,
        users: tuple[UserModel, UserModel],
        access_tokens: tuple[str, str],
    ) -> None:
        first_user, second_user = users
        first_token, _ = access_tokens
        response = client.put(
            f'{self.BASE_URI}/{first_user.id}',
            headers={'Authorization': f'Bearer {first_token}'},
            json={
                'username': 'username',
                'email': second_user.email,
                'password': 'password',
            },
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {
            'error': 'ConflictError',
            'detail': 'username or email already in use.',
        }

    def test_patch_user_successful(
        self, client: TestClient, user: UserModel, access_token: str
    ) -> None:
        body_request = {'username': 'username'}
        response = client.patch(
            f'{self.BASE_URI}/{user.id}',
            headers={'Authorization': f'Bearer {access_token}'},
            json=body_request,
        )

        data = response.json()
        assert response.status_code == HTTPStatus.OK
        assert data['id'] == str(user.id)
        assert data['username'] == body_request['username']
        assert data['email'] == user.email

    def test_patch_other_user_failure(
        self, client: TestClient, access_token: str
    ) -> None:
        body_request = {'username': 'username'}
        response = client.patch(
            f'{self.BASE_URI}/{uuid7()}',
            headers={'Authorization': f'Bearer {access_token}'},
            json=body_request,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_patch_user_with_same_username_failure(
        self,
        client: TestClient,
        users: tuple[UserModel, UserModel],
        access_tokens: tuple[str, str],
    ) -> None:
        first_user, second_user = users
        first_token, _ = access_tokens
        response = client.patch(
            f'{self.BASE_URI}/{first_user.id}',
            headers={'Authorization': f'Bearer {first_token}'},
            json={'username': second_user.username},
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {
            'error': 'ConflictError',
            'detail': 'username or email already in use.',
        }

    def test_patch_user_with_same_email_failure(
        self,
        client: TestClient,
        users: tuple[UserModel, UserModel],
        access_tokens: tuple[str, str],
    ) -> None:
        first_user, second_user = users
        first_token, _ = access_tokens
        response = client.patch(
            f'{self.BASE_URI}/{first_user.id}',
            headers={'Authorization': f'Bearer {first_token}'},
            json={'email': second_user.email},
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {
            'error': 'ConflictError',
            'detail': 'username or email already in use.',
        }

    def test_delete_user_successful(
        self, client: TestClient, user: UserModel, access_token: str
    ) -> None:
        response = client.delete(
            f'{self.BASE_URI}/{user.id}',
            headers={'Authorization': f'Bearer {access_token}'},
        )

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.content == b''

    def test_delete_other_user_failure(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.delete(
            f'{self.BASE_URI}/{uuid7()}',
            headers={'Authorization': f'Bearer {access_token}'},
        )

        assert response.status_code == HTTPStatus.FORBIDDEN
