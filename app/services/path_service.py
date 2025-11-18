from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.exceptions.erros import NotFoundError
from app.repositories.path_repository import PathRepository
from app.schemas.path_schema import PathCreate, PathResponse, PathResponseList


class PathService:
    def __init__(
        self,
        repository: Annotated[PathRepository, Depends()],
    ) -> None:
        self.repository = repository

    async def get_all_paths(self) -> PathResponseList:
        return PathResponseList(data=await self.repository.search_all())

    async def get_path_by_id(self, path_id: UUID) -> PathResponse:
        path = await self.repository.search(path_id)
        if path is None:
            raise NotFoundError
        return path

    async def create_path(self, path: PathCreate) -> PathResponse:
        return await self.repository.create(path.model_dump())

    async def delete_path(self, path_id: UUID) -> None:
        path = await self.repository.search(path_id)
        if path is None:
            raise NotFoundError
        return await self.repository.delete(path)
