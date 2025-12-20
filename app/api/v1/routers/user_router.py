from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends

from app.exceptions.erros import (
    ConflictError,
    ContentError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from app.models.user_model import UserModel
from app.schemas.examples.user_example import UserExample
from app.schemas.user_schema import (
    UserCreate,
    UserPatch,
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

one_resource_responses: dict[int | str, dict[str, Any]] = {
    HTTPStatus.UNAUTHORIZED: {
        'description': HTTPStatus.UNAUTHORIZED.description,
        'model': UnauthorizedError.schema(),
    },
    HTTPStatus.FORBIDDEN: {
        'description': HTTPStatus.FORBIDDEN.description,
        'model': ForbiddenError.schema(),
    },
    HTTPStatus.NOT_FOUND: {
        'description': HTTPStatus.NOT_FOUND.description,
        'model': NotFoundError.schema(),
    },
}


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
    responses=one_resource_responses,
)
async def get_user(
    service: InjectService, user_id: UUID, current_user: CurrentUser
) -> UserResponse:
    return await service.get_user(user_id, current_user)


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    responses=one_resource_responses,
)
async def update_user(
    service: InjectService,
    user_id: UUID,
    updated_user: UserUpdate,
    current_user: CurrentUser,
) -> UserResponse:
    return await service.update_user(user_id, updated_user, current_user)


@router.patch(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    responses=one_resource_responses,
)
async def patch_user(
    service: InjectService,
    user_id: UUID,
    patched_user: UserPatch,
    current_user: CurrentUser,
) -> UserResponse:
    return await service.patch_user(user_id, patched_user, current_user)


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
    responses=one_resource_responses,
)
async def delete_user(
    service: InjectService,
    user_id: UUID,
    current_user: CurrentUser,
) -> None:
    return await service.delete_user(user_id, current_user)
