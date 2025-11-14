from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, status

from app.schemas.examples.path_example import PathExample
from app.schemas.path_schema import PathCreate, PathResponse, PathResponseList
from app.services.path_service import PathService

PathServices = Annotated[PathService, Depends(PathService)]

router = APIRouter(
    prefix='/api/v1/paths',
    tags=['path'],
)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_paths(
    service: PathServices,
) -> PathResponseList:
    return await service.get_all_paths()


@router.get('/{path_id}', status_code=status.HTTP_200_OK)
async def get_path(
    path_id: UUID,
    service: PathServices,
) -> PathResponse:
    return await service.get_path_by_id(path_id)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_path(
    service: PathServices,
    path: Annotated[PathCreate, Body(openapi_examples=PathExample)],
) -> PathResponse:
    return await service.create_path(path)


@router.delete(
    '/{path_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_path(
    path_id: UUID,
    service: PathServices,
) -> None:
    return await service.delete_path(path_id)
