from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode
from pwdlib import PasswordHash

from app.core.settings import settings
from app.exceptions.erros import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserResponse

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

        user_data['password'] = self.__get_hashed_password(
            user_data['password']
        )
        db_user = await self.repository.create(user_data)
        return UserResponse.model_validate(db_user)

    async def get_user(
        self, user_id: UUID, user: UserResponse
    ) -> UserResponse:
        if user.id != user_id:
            raise ForbiddenError
        return user

    @classmethod
    def __get_hashed_password(cls, plain_password: str) -> str:
        return pwd_context.hash(plain_password)

    @classmethod
    def check_password(cls, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    service: Annotated[UserService, Depends()],
    token: str = Depends(oauth2_scheme),
) -> UserResponse:
    try:
        payload = decode(
            token, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM
        )
        username_sub = payload.get('sub')
        if username_sub is None:
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

    return UserResponse.model_validate(user_db)
