from datetime import datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from jwt import encode

from app.core.settings import settings
from app.exceptions.erros import UnauthorizedError
from app.repositories.user_repository import UserRepository
from app.schemas.token_schema import TokenResponse
from app.services.user_service import UserService


class AuthService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends()],
        user_service: Annotated[UserService, Depends()],
    ) -> None:
        self.user_repository = user_repository
        self.user_service = user_service

    def create_token_by_sub(self, sub: str) -> TokenResponse:
        expire_time = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
            minutes=settings.TOKEN_EXPIRE_MINUTES
        )
        claims = {'sub': sub, 'exp': expire_time}
        access_token = encode(
            claims, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM
        )
        return TokenResponse(access_token=access_token)

    async def create_token_by_form(
        self, form: OAuth2PasswordRequestForm
    ) -> TokenResponse:
        user_db = await self.user_repository.search_by_field(
            'username', form.username
        )
        if user_db is None:
            raise UnauthorizedError(
                message='username or password doesnt match'
            )

        if not self.user_service.check_password(
            form.password, user_db.password
        ):
            raise UnauthorizedError(
                message='username or password doesnt match'
            )

        return self.create_token_by_sub(user_db.username)
