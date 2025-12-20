from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.exceptions.erros import NotFoundError
from app.models.user_model import UserModel
from app.schemas.filters_params_schema import SortEnum
from app.schemas.user_schema import CurrentUserResponse


class UserRepository:
    def __init__(
        self, db_session: Annotated[AsyncSession, Depends(get_session)]
    ) -> None:
        self.db_session = db_session

    async def add_commit_refresh_changes(self, user: UserModel) -> UserModel:
        self.db_session.add(user)
        await self.db_session.commit()
        await self.db_session.refresh(user)
        return user

    async def create(self, user: dict[str, Any]) -> UserModel:
        user_model = UserModel(**user)
        return await self.add_commit_refresh_changes(user_model)

    async def update(self, user: CurrentUserResponse) -> UserModel:
        db_user = await self.search_by_field('id', user.id)
        if db_user is None:
            raise NotFoundError

        db_user.username = user.username
        db_user.email = user.email
        db_user.password = user.password

        return await self.add_commit_refresh_changes(db_user)

    async def search_all(
        self, skip: int, limit: int, order_by: str, arranging: SortEnum
    ) -> Sequence[UserModel]:
        orderned_by = (
            asc(order_by) if arranging == SortEnum.ASC else desc(order_by)
        )
        result = await self.db_session.execute(
            select(UserModel).offset(skip).limit(limit).order_by(orderned_by)
        )
        return result.scalars().all()

    async def search_by_field(
        self,
        field: str,
        value: Any,  # noqa: ANN401
    ) -> UserModel | None:
        result = await self.db_session.execute(
            select(UserModel).where(getattr(UserModel, field) == value)
        )
        return result.scalar_one_or_none()
