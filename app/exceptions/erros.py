from http import HTTPStatus
from typing import Any, Literal

from pydantic import BaseModel, create_model


class BaseError(Exception):
    __schema: BaseModel | None = None

    def __init__(
        self,
        message: dict,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    @classmethod
    def schema(cls) -> BaseModel:
        if cls.__schema is not None:
            return cls.__schema

        model = create_model(
            cls.__name__,
            error=(Literal[cls.__name__]),
            detail=(str | list[dict[str, Any]], ...),
        )
        cls.__schema = model

        return cls.__schema


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
