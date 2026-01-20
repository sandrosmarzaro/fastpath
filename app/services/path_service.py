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
from app.services.cache_service import CacheService
from app.solvers.ortools_solver import ORToolsSolver


class PathService:
    def __init__(
        self,
        repository: Annotated[PathRepository, Depends()],
        cache: Annotated[CacheService, Depends()],
    ) -> None:
        self.repository = repository
        self.cache = cache

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
        coords = [path.pickup, *path.dropoff]
        all_pairs = []
        all_cache_keys = []

        for i, coord1 in enumerate(coords):
            for j in range(i + 1, len(coords)):
                coord2 = coords[j]
                pair = (i, j)
                all_pairs.append(pair)
                all_cache_keys.append(
                    self._make_pair_cache_key(coord1, coord2)
                )

        cached_values = await self.cache.get_many('dist', all_cache_keys)

        pairs_cost = {}
        missing_pairs = []
        missing_pair_indices = []

        for pair, cache_key in zip(all_pairs, all_cache_keys, strict=False):
            cached_cost = (
                cached_values.get(cache_key) if cached_values else None
            )
            if cached_cost is not None:
                pairs_cost[pair] = float(cached_cost)
            else:
                i, j = pair
                missing_pairs.append((coords[i], coords[j]))
                missing_pair_indices.append(pair)

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

            await self.cache.set_many(
                prefix='dist',
                keys=[
                    self._make_pair_cache_key(pair[0], pair[1])
                    for pair in missing_pairs
                ],
                values=[
                    str(missing_cost_matrix[i * 2][i * 2 + 1])
                    for i in range(len(missing_pairs))
                ],
            )

            for i, pair_idx in enumerate(missing_pair_indices):
                pairs_cost[pair_idx] = missing_cost_matrix[i * 2][i * 2 + 1]

        matrix = self._build_cost_matrix(pairs_cost, len(coords))

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

    def _make_pair_cache_key(
        self, coord1: CoordinatesCreate, coord2: CoordinatesCreate
    ) -> str:
        index1 = self._convert_coord_to_h3_index(coord1)
        index2 = self._convert_coord_to_h3_index(coord2)
        return f'dist:{index1}:{index2}'

    def _build_cost_matrix(
        self,
        pairs_cost: dict[tuple[int, int], float],
        n: int,
    ) -> list[list[float]]:
        matrix = [[0.0] * n for _ in range(n)]

        for (i, j), cost in pairs_cost.items():
            matrix[i][j] = cost
            matrix[j][i] = cost

        return matrix

    async def delete_path(self, path_id: UUID, user: UserModel) -> None:
        path = await self.repository.search(path_id)
        if path is None:
            raise NotFoundError
        if path.user_id != user.id:
            raise ForbiddenError
        return await self.repository.delete(path)
