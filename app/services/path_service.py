from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Depends
from h3 import latlng_to_cell

from app.core.settings import settings
from app.exceptions.erros import ForbiddenError, NotFoundError
from app.models.user_model import UserModel
from app.repositories.path_repository import PathRepository
from app.schemas.coordinates_schema import CoordinatesCreate
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
        pairs_cost = {}
        missing_pairs = []
        coords = [path.pickup, *path.dropoff]
        for i, coord1 in enumerate(coords):
            for coord2 in coords[i + 1 :]:
                key = self._make_pair_cache_key(coord1, coord2)
                # TODO @sandrosmarzaro: retrieve from cache
                # 001
                cached_cost = ...
                if cached_cost:
                    pairs_cost[(coord1, coord2)] = int(cached_cost)
                else:
                    missing_pairs.append((coord1, coord2))

        if missing_pairs:
            formatted_coords = [
                f'{coord.lng},{coord.lat}'
                for pair in missing_pairs
                for coord in pair
            ]
            coords_url = ';'.join(formatted_coords)
            base_url = settings.OSRM_URL + 'table/v1/driving/'
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=f'{base_url}{coords_url}',
                    params={'annotations': 'duration,distance'},
                )
                response.raise_for_status()
            missing_cost_matrix = response.json()['durations']
            # TODO @sandrosmarzaro: store in cache
            # 002

        matrix = self._build_cost_matrix(pairs_cost, missing_cost_matrix)

        optimal_route = ORToolsSolver.solve(matrix)

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

    def _convert_coord_to_h3_index(self, coord: CoordinatesCreate) -> str:
        return latlng_to_cell(coord.lat, coord.lng, settings.H3_RESOLUTION)

    async def _make_pair_cache_key(
        self, coord1: CoordinatesCreate, coord2: CoordinatesCreate
    ) -> str:
        index1 = self._convert_coord_to_h3_index(coord1)
        index2 = self._convert_coord_to_h3_index(coord2)
        return f'dist:{index1}:{index2}'

    def _build_cost_matrix(
        self,
        pairs_cost: dict[str, int],
        missing_cost_matrix: dict[str, list[int]],
    ) -> dict[str, list[int]]:
        # TODO @sandrosmarzaro: implement the logic to build the full cost matrix
        # 003
        pass

    async def delete_path(self, path_id: UUID, user: UserModel) -> None:
        path = await self.repository.search(path_id)
        if path is None:
            raise NotFoundError
        if path.user_id != user.id:
            raise ForbiddenError
        return await self.repository.delete(path)
