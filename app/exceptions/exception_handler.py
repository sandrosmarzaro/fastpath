from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.erros import BaseError


async def __create_handle_error(
    request: Request,  # noqa: ARG001
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={'error': type(exc).__name__, 'detail': exc.message},
    )


async def __global_internal_handle_error(
    request: Request,  # noqa: ARG001
    exc: HTTPException,
) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={
            'error': type(exc).__name__,
            'detail': HTTPStatus.INTERNAL_SERVER_ERROR.description,
        },
    )


async def __global_validation_handle_error(
    request: Request,  # noqa: ARG001
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_CONTENT,
        content={
            'error': type(exc).__name__,
            'detail': jsonable_encoder(exc.errors()),
        },
    )


def add_exceptions_handler(app: FastAPI) -> None:
    app.add_exception_handler(
        HTTPStatus.INTERNAL_SERVER_ERROR,
        __global_internal_handle_error,
    )
    app.add_exception_handler(
        RequestValidationError,
        __global_validation_handle_error,
    )
    app.add_exception_handler(BaseError, __create_handle_error)
