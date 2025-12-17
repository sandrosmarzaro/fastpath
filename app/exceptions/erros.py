from functools import lru_cache
from http import HTTPStatus
from typing import Any, Literal

from pydantic import BaseModel, create_model


class BaseError(Exception):
    def __init__(
        self,
        message: str | dict,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.headers = headers

    @classmethod
    @lru_cache
    def schema(cls) -> type[BaseModel]:
        return create_model(
            cls.__name__,
            error=(Literal[cls.__name__], ...),
            detail=(str | list[dict[str, Any]], ...),
        )


class NotFoundError(BaseError):
    def __init__(
        self,
        message: str = HTTPStatus.NOT_FOUND.description,
        status_code: int = HTTPStatus.NOT_FOUND,
    ) -> None:
        super().__init__(message, status_code)


class ContentError(BaseError):
    def __init__(
        self,
        message: str = HTTPStatus.UNPROCESSABLE_CONTENT.description,
        status_code: int = HTTPStatus.UNPROCESSABLE_CONTENT,
    ) -> None:
        super().__init__(message, status_code)


class UnauthorizedError(BaseError):
    def __init__(
        self,
        message: str = HTTPStatus.UNAUTHORIZED.description,
        status_code: int = HTTPStatus.UNAUTHORIZED,
    ) -> None:
        super().__init__(
            message,
            status_code,
            headers={'WWW-Authenticate': 'Bearer'},
        )


class ConflictError(BaseError):
    def __init__(
        self,
        message: str = HTTPStatus.CONFLICT.description,
        status_code: int = HTTPStatus.CONFLICT,
    ) -> None:
        super().__init__(message, status_code)


class ForbiddenError(BaseError):
    def __init__(
        self,
        message: str = HTTPStatus.FORBIDDEN.description,
        status_code: int = HTTPStatus.FORBIDDEN,
    ) -> None:
        super().__init__(message, status_code)
