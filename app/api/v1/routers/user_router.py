from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query

from app.exceptions.erros import ConflictError, ContentError, UnauthorizedError
from app.schemas.examples.user_example import UserExample
from app.schemas.filters_params_schema import (
    PaginationSortingFilters as Filters,
)
from app.schemas.user_schema import UserCreate, UserResponse, UserResponseList
from app.services.user_service import UserService, get_current_user

UserServices = Annotated[UserService, Depends()]

router = APIRouter(
    prefix='/api/v1/users',
    tags=['users'],
    responses={
        HTTPStatus.UNPROCESSABLE_CONTENT: {
            'description': HTTPStatus.UNPROCESSABLE_CONTENT.description,
            'model': ContentError.schema(),
        },
        HTTPStatus.UNAUTHORIZED: {
            'description': HTTPStatus.UNAUTHORIZED.description,
            'model': UnauthorizedError.schema(),
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
    '/', status_code=HTTPStatus.OK, dependencies=[Depends(get_current_user)]
)
async def get_users(
    service: UserServices,
    filters: Annotated[Filters, Query()],
) -> UserResponseList:
    return await service.get_all_users(
        filters.skip,
        filters.limit,
        filters.order_by,
        filters.arranging,
    )
