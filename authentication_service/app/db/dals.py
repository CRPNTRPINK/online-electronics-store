from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from authentication_service.app.db.models import User


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, name, surname, email, hashed_password) -> User:
        new_user = User(name=name, surname=surname, email=email, hashed_password=hashed_password)
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> Optional[UUID]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        found_user_id = res.fetchone()
        if found_user_id is not None:
            return found_user_id[0]

    async def get_user_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        found_user_id = res.fetchone()
        if found_user_id is not None:
            return found_user_id[0]

    async def update_user(self, user_id: UUID, **kwargs) -> Optional[User]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(kwargs)
            .returning(User)
        )
        res = await self.db_session.execute(query)
        updated_user = res.fetchone()
        if updated_user is not None:
            return updated_user[0]
