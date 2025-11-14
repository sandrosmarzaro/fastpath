from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.repositories.path_repository import PathRepository
from app.schemas.path_schema import PathCreate, PathResponse, PathResponseList


class PathService:
    def __init__(
        self,
        repository: PathRepository = Depends(),
    ) -> None:
        self.repository = repository

    async def get_all_paths(self) -> PathResponseList:
        return PathResponseList(data=await self.repository.search_all())

    async def get_path_by_id(self, path_id: UUID) -> PathResponse:
        path = await self.repository.search(path_id)
        if path is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return path

    async def create_path(self, path: PathCreate) -> PathResponse:
        return await self.repository.create(path.model_dump())

    async def delete_path(self, path_id: UUID) -> None:
        path = await self.repository.search(path_id)
        if path is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return await self.repository.delete(path)
