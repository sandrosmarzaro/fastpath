from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CoordinatesBase(BaseModel):
    lat: float = Field(..., ge=-90, le=90, title='Latitude')
    lng: float = Field(..., ge=-180, le=180, title='Longitude')

    @field_validator('lat', 'lng')
    @classmethod
    def round_coordinates(cls, v: float) -> float:
        return round(v, 7)


class CoordinatesCreate(CoordinatesBase):
    pass


class CoordinatesResponse(BaseModel):
    id: UUID
    lat: float
    lng: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
