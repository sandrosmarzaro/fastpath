from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError

from app.core.settings import settings
from app.exceptions.erros import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from app.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import (
    UserCreate,
    UserPatch,
    UserResponse,
    UserUpdate,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token')

pwd_context = PasswordHash.recommended()


class UserService:
    def __init__(
        self, repository: Annotated[UserRepository, Depends()]
    ) -> None:
        self.repository = repository

    async def create_user(self, user: UserCreate) -> UserResponse:
        user_data = user.model_dump()
        same_username = await self.repository.search_by_field(
            'username', user_data['username']
        )
        if same_username:
            raise ConflictError(message='username already in use.')

        same_email = await self.repository.search_by_field(
            'email', user_data['email']
        )
        if same_email:
            raise ConflictError(message='email already in use.')

        user_data['password'] = self.get_hashed_password(user_data['password'])
        db_user = await self.repository.create(user_data)
        return UserResponse.model_validate(db_user)

    async def get_user(self, user_id: UUID, user: UserModel) -> UserResponse:
        if user.id != user_id:
            raise ForbiddenError
        return UserResponse.model_validate(user)

    async def update_user(
        self,
        user_id: UUID,
        updated_user: UserUpdate,
        current_user: UserModel,
    ) -> UserResponse:
        if current_user.id != user_id:
            raise ForbiddenError

        current_user.username = updated_user.username
        current_user.email = updated_user.email
        current_user.password = self.get_hashed_password(updated_user.password)
        try:
            updated_model = await self.repository.add_commit_refresh_changes(
                current_user
            )
            return UserResponse.model_validate(updated_model)
        except IntegrityError as e:
            raise ConflictError(
                message='username or email already in use.'
            ) from e

    async def patch_user(
        self,
        user_id: UUID,
        patched_user: UserPatch,
        current_user: UserModel,
    ) -> UserResponse:
        if current_user.id != user_id:
            raise ForbiddenError

        patched_data = patched_user.model_dump(exclude_unset=True)
        if 'password' in patched_data:
            patched_data['password'] = self.get_hashed_password(
                patched_data['password']
            )

        for key, value in patched_data.items():
            setattr(current_user, key, value)

        try:
            patched_model = await self.repository.add_commit_refresh_changes(
                current_user
            )
            return UserResponse.model_validate(patched_model)
        except IntegrityError as e:
            raise ConflictError(
                message='username or email already in use.'
            ) from e

    async def delete_user(
        self, user_id: UUID, current_user: UserModel
    ) -> None:
        if current_user.id != user_id:
            raise ForbiddenError

        return await self.repository.delete(current_user)

    @classmethod
    def get_hashed_password(cls, plain_password: str) -> str:
        return pwd_context.hash(plain_password)

    @classmethod
    def check_password(cls, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    service: Annotated[UserService, Depends()],
    token: str = Depends(oauth2_scheme),
) -> UserModel:
    try:
        payload = decode(
            token, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM
        )
        username_sub = payload.get('sub')
        if not username_sub:
            raise UnauthorizedError(message='could not validate credentials')
    except (DecodeError, ExpiredSignatureError) as e:
        raise UnauthorizedError(
            message='could not validate credentials'
        ) from e

    user_db = await service.repository.search_by_field(
        'username', username_sub
    )
    if user_db is None:
        raise NotFoundError

    return user_db
