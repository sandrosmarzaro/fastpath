from typing import Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.models.coordinates_model import CoordinatesModel
from app.models.path_model import PathModel


class PathRepository:
    def __init__(self, db_session: AsyncSession) -> None:
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

    async def search(self, path_id: UUID) -> PathModel:
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

    async def search_all(self) -> list[PathModel]:
        result = await self.db_session.execute(
            select(PathModel)
            .join(PathModel.pickup)
            .options(
                selectinload(PathModel.pickup),
                selectinload(PathModel.dropoff),
            ),
        )
        return result.scalars().all()

    async def delete(self, path_id: UUID) -> None:
        await self.db_session.execute(
            select(PathModel).where(PathModel.id == path_id),
        )


def get_path_repository(
    db_session: AsyncSession = Depends(get_session),
) -> PathRepository:
    return PathRepository(db_session)
