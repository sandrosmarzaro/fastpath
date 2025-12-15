from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class FiltersParamsBase(BaseModel):
    pass


class PaginationFilters(FiltersParamsBase):
    skip: int = Field(
        default=0,
        ge=0,
        description='how many rows do want to jump',
    )
    limit: int = Field(
        default=10,
        gt=0,
        le=100,
        description='how many rows you get per page',
    )


class SortEnum(str, Enum):
    ASC = 'asc'
    DESC = 'desc'


class PaginationSortingFilters(PaginationFilters):
    order_by: Literal['created_at', 'updated_at'] = 'created_at'
    arranging: SortEnum = Field(
        default=SortEnum.DESC,
        json_schema_extra={'enum': ['asc', 'desc']},
        description='choice to order by the older or younger',
    )
