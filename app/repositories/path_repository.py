from collections.abc import Sequence
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.models.coordinates_model import CoordinatesModel
from app.models.path_model import PathModel
from app.schemas.filters_params_schema import SortEnum


class PathRepository:
    def __init__(
        self,
        db_session: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db_session = db_session

    async def create(self, path: dict[str, Any]) -> PathModel:
        pickup_data = path.pop('pickup')
        dropff_data_list = path.pop('dropoff')

        pickup_coords = CoordinatesModel(**pickup_data)
        self.db_session.add(pickup_coords)
        await self.db_session.commit()
        await self.db_session.refresh(pickup_coords)

        new_path = PathModel(pickup_id=pickup_coords.id, **path)
        self.db_session.add(new_path)

        dropoff_coords_list = []
        for dropoff_data in dropff_data_list:
            dropoff_coords = CoordinatesModel(**dropoff_data)
            dropoff_coords_list.append(dropoff_coords)

        self.db_session.add_all(dropoff_coords_list)
        new_path.dropoff = dropoff_coords_list

        await self.db_session.commit()
        await self.db_session.refresh(
            new_path,
            attribute_names=['pickup', 'dropoff'],
        )

        return new_path

    async def search(self, path_id: UUID) -> PathModel | None:
        result = await self.db_session.execute(
            select(PathModel)
            .join(PathModel.pickup)
            .options(
                selectinload(PathModel.pickup),
                selectinload(PathModel.dropoff),
            )
            .where(PathModel.id == path_id),
        )
        return result.scalar_one_or_none()

    async def search_all_by_user(
        self,
        user: UUID,
        skip: int,
        limit: int,
        order_by: str,
        arranging: SortEnum,
    ) -> Sequence[PathModel]:
        orderned_by = (
            asc(order_by) if arranging == SortEnum.ASC else desc(order_by)
        )
        result = await self.db_session.execute(
            select(PathModel)
            .join(PathModel.pickup)
            .options(
                selectinload(PathModel.pickup),
                selectinload(PathModel.dropoff),
            )
            .where(PathModel.user_id == user)
            .offset(skip)
            .limit(limit)
            .order_by(orderned_by)
        )
        return result.scalars().all()

    async def delete(self, path: PathModel) -> None:
        await self.db_session.delete(path)
        await self.db_session.commit()
