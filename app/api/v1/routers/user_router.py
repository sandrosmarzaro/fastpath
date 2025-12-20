from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends

from app.exceptions.erros import (
    ConflictError,
    ContentError,
    ForbiddenError,
    UnauthorizedError,
)
from app.models.user_model import UserModel
from app.schemas.examples.user_example import UserExample
from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService, get_current_user

InjectService = Annotated[UserService, Depends()]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]

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
    service: InjectService,
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
    service: InjectService, user_id: UUID, current_user: CurrentUser
) -> UserResponse:
    return await service.get_user(user_id, current_user)


@router.put(
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
async def update_user(
    service: InjectService,
    user_id: UUID,
    updated_user: UserUpdate,
    current_user: CurrentUser,
) -> UserResponse:
    return await service.update_user(user_id, updated_user, current_user)
