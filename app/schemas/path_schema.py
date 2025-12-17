from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.coordinates_schema import (
    CoordinatesCreate,
    CoordinatesResponse,
)


class PathBase(BaseModel):
    pass


class PathCreate(PathBase):
    pickup: CoordinatesCreate
    dropoff: list[CoordinatesCreate]


class PathResponse(PathBase):
    id: UUID
    user_id: UUID
    pickup: CoordinatesResponse
    dropoff: list[CoordinatesResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PathResponseList(PathBase):
    data: list[PathResponse]
