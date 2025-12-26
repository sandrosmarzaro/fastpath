from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Depends

from app.core.settings import settings
from app.exceptions.erros import ForbiddenError, NotFoundError
from app.models.user_model import UserModel
from app.repositories.path_repository import PathRepository
from app.schemas.filters_params_schema import SortEnum
from app.schemas.path_schema import PathCreate, PathResponse, PathResponseList
from app.solvers.ortools_solver import ORToolsSolver


class PathService:
    def __init__(
        self,
        repository: Annotated[PathRepository, Depends()],
    ) -> None:
        self.repository = repository

    async def get_all_paths_by_user(
        self,
        user: UserModel,
        skip: int,
        limit: int,
        order_by: str,
        arranging: SortEnum,
    ) -> PathResponseList:
        db_paths = await self.repository.search_all_by_user(
            user.id, skip, limit, order_by, arranging
        )
        return PathResponseList(
            data=[PathResponse.model_validate(path) for path in db_paths]
        )

    async def get_path_by_id(
        self, path_id: UUID, user: UserModel
    ) -> PathResponse:
        db_path = await self.repository.search(path_id)
        if db_path is None:
            raise NotFoundError
        if db_path.user_id != user.id:
            raise ForbiddenError
        return PathResponse.model_validate(db_path)

    async def create_path(
        self, user: UserModel, path: PathCreate
    ) -> PathResponse:
        base_url = settings.OSRM_URL + 'table/v1/driving/'
        coords = [f'{path.pickup.lng},{path.pickup.lat}']
        coords.extend(f'{coord.lng},{coord.lat}' for coord in path.dropoff)
        coords_url = ';'.join(coords)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f'{base_url}{coords_url}',
                params={'annotations': 'duration,distance'},
            )
            response.raise_for_status()
        durantion_matrix = response.json()['durations']

        optimal_route = ORToolsSolver.solve(durantion_matrix)

        reordered_dropoffs = [
            path.dropoff[i - 1] for i in optimal_route if i > 0
        ]
        path_data = path.model_dump()
        path_data['dropoff'] = [
            dropoff.model_dump() if hasattr(dropoff, 'model_dump') else dropoff
            for dropoff in reordered_dropoffs
        ]
        path_data['user_id'] = user.id

        db_path = await self.repository.create(path_data)
        return PathResponse.model_validate(db_path)

    async def delete_path(self, path_id: UUID, user: UserModel) -> None:
        path = await self.repository.search(path_id)
        if path is None:
            raise NotFoundError
        if path.user_id != user.id:
            raise ForbiddenError
        return await self.repository.delete(path)
