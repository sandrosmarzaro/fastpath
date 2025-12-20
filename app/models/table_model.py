from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as UUIDSQL
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid6 import uuid7


class TableModel(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(UUIDSQL, primary_key=True, default=uuid7)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
    )
