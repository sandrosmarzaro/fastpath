from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends

from app.api.v1.routers.auth_router import CurrentUser
from app.exceptions.erros import (
    ConflictError,
    ContentError,
    ForbiddenError,
    UnauthorizedError,
)
from app.schemas.examples.user_example import UserExample
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.user_service import UserService

UserServices = Annotated[UserService, Depends()]

router = APIRouter(
    prefix='/api/v1/users',
    tags=['users'],
    responses={
        HTTPStatus.UNPROCESSABLE_CONTENT: {
            'description': HTTPStatus.UNPROCESSABLE_CONTENT.description,
            'model': ContentError.schema(),
        },
    },
)


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.CONFLICT: {
            'description': HTTPStatus.CONFLICT.description,
            'model': ConflictError.schema(),
        },
    },
)
async def create_user(
    service: UserServices,
    user: Annotated[UserCreate, Body(openapi_examples=UserExample)],
) -> UserResponse:
    return await service.create_user(user)


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.UNAUTHORIZED: {
            'description': HTTPStatus.UNAUTHORIZED.description,
            'model': UnauthorizedError.schema(),
        },
        HTTPStatus.FORBIDDEN: {
            'description': HTTPStatus.FORBIDDEN.description,
            'model': ForbiddenError.schema(),
        },
    },
)
async def get_user(
    service: UserServices, user_id: UUID, current_user: CurrentUser
) -> UserResponse:
    return await service.get_user(user_id, current_user)
