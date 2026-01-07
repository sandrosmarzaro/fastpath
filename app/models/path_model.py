from uuid import UUID

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.coordinates_model import CoordinatesModel
from app.models.table_model import TableModel
from app.models.user_model import UserModel

dropoff_coordinates = Table(
    'dropoff_coordinates',
    TableModel.metadata,
    Column('coordinates_id', ForeignKey('coordinates.id'), primary_key=True),
    Column('path_id', ForeignKey('paths.id'), primary_key=True),
)


class PathModel(TableModel):
    __tablename__ = 'paths'

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
    )
    user: Mapped[UserModel] = relationship(
        back_populates='paths',
        lazy='raise',
    )
    pickup_id: Mapped[UUID] = mapped_column(
        ForeignKey('coordinates.id'),
        nullable=False,
    )
    pickup: Mapped[CoordinatesModel] = relationship(
        back_populates='paths',
        lazy='raise',
        cascade='all, delete-orphan',
    )
    dropoff: Mapped[list[CoordinatesModel]] = relationship(
        secondary=dropoff_coordinates,
        lazy='raise',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return (
            f'path(id={self.id}, user_id(id={self.user_id}, '
            f'pickup_id={self.pickup_id}, dropoff={self.dropoff}, '
            f'created_at={self.created_at}, updated_at={self.updated_at})'
        )
