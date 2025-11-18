from http import HTTPStatus


class BaseError(Exception):
    def __init__(
        self,
        message: dict,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(BaseError):
    def __init__(
        self,
        message: str = HTTPStatus.NOT_FOUND.description,
        status_code: int = HTTPStatus.NOT_FOUND,
    ) -> None:
        super().__init__(message, status_code)
