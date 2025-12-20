from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query

from app.exceptions.erros import (
    ContentError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from app.models.user_model import UserModel
from app.schemas.examples.path_example import PathExample
from app.schemas.filters_params_schema import (
    PaginationSortingFilters as Filters,
)
from app.schemas.path_schema import PathCreate, PathResponse, PathResponseList
from app.services.path_service import PathService
from app.services.user_service import get_current_user

InjectService = Annotated[PathService, Depends()]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]

router = APIRouter(
    prefix='/api/v1/paths',
    tags=['paths'],
    dependencies=[Depends(get_current_user)],
    responses={
        HTTPStatus.UNPROCESSABLE_CONTENT: {
            'description': HTTPStatus.UNPROCESSABLE_CONTENT.description,
            'model': ContentError.schema(),
        },
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


@router.get('/', status_code=HTTPStatus.OK)
async def get_paths(
    service: InjectService,
    user: CurrentUser,
    filters: Annotated[Filters, Query()],
) -> PathResponseList:
    return await service.get_all_paths_by_user(
        user,
        filters.skip,
        filters.limit,
        filters.order_by,
        filters.arranging,
    )


@router.get(
    '/{path_id}',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.NOT_FOUND: {
            'description': HTTPStatus.NOT_FOUND.description,
            'model': NotFoundError.schema(),
        },
    },
)
async def get_path(
    path_id: UUID,
    service: InjectService,
    user: CurrentUser,
) -> PathResponse:
    return await service.get_path_by_id(path_id, user)


@router.post('/', status_code=HTTPStatus.CREATED)
async def create_path(
    service: InjectService,
    user: CurrentUser,
    path: Annotated[PathCreate, Body(openapi_examples=PathExample)],
) -> PathResponse:
    return await service.create_path(user, path)


@router.delete(
    '/{path_id}',
    status_code=HTTPStatus.NO_CONTENT,
    responses={
        HTTPStatus.NOT_FOUND: {
            'description': HTTPStatus.NOT_FOUND.description,
            'model': NotFoundError.schema(),
        },
    },
)
async def delete_path(
    path_id: UUID,
    user: CurrentUser,
    service: InjectService,
) -> None:
    return await service.delete_path(path_id, user)
