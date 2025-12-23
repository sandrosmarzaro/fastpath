from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.user_model import UserModel


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

    async def search_by_field(
        self,
        field: str,
        value: Any,  # noqa: ANN401
    ) -> UserModel | None:
        result = await self.db_session.execute(
            select(UserModel).where(getattr(UserModel, field) == value)
        )
        return result.scalar_one_or_none()

    async def delete(self, user: UserModel) -> None:
        await self.db_session.delete(user)
        await self.db_session.commit()
