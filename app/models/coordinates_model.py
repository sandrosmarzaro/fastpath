from typing import TYPE_CHECKING

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.table_model import TableModel

if TYPE_CHECKING:
    from app.models.path_model import PathModel


class CoordinatesModel(TableModel):
    __tablename__ = 'coordinates'

    lat: Mapped[float] = mapped_column(Numeric(9, 7), nullable=False)
    lng: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)

    paths: Mapped[list['PathModel']] = relationship(
        back_populates='pickup',
        lazy='raise',
    )

    def __repr__(self) -> str:
        return (
            f'coordinates(id={self.id}, lat={self.lat}, lng={self.lng}, '
            'created_at={self.created_at}, updated_at={self.updated_at})'
        )
