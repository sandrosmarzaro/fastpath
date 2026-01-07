from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.table_model import TableModel

if TYPE_CHECKING:
    from app.models.path_model import PathModel


class UserModel(TableModel):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))

    paths: Mapped[list['PathModel']] = relationship(
        back_populates='user',
        lazy='raise',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return (
            f'user(id={self.id}, username={self.username}, email={self.email} '
            'created_at={self.created_at}, updated_at={self.updated_at})'
        )
