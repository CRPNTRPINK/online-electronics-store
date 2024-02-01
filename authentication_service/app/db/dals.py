from typing import Optional
from uuid import UUID

from sqlalchemy import Row, Sequence, and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, name: str, surname: str, email: str, hashed_password: str) -> User:
        new_user = User(name=name, surname=surname, email=email.lower(), hashed_password=hashed_password)
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
        if deleted_user_id_row:
            return deleted_user_id_row[0]

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        found_user_id = res.fetchone()
        if found_user_id:
            return found_user_id[0]

    async def get_user_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email.lower())
        res = await self.db_session.execute(query)
        found_user_id = res.fetchone()
        if found_user_id:
            return found_user_id[0]

    async def get_users(self) -> Sequence[Row[tuple[User]]]:
        query = select(User)
        res = await self.db_session.execute(query)
        users = res.fetchall()
        if users:
            return users

    async def update_user(self, user_id: UUID, **kwargs) -> Optional[User]:
        if kwargs.get('email'):
            kwargs['email'] = kwargs['email'].lower()
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(kwargs)
            .returning(User)
        )
        res = await self.db_session.execute(query)
        updated_user = res.fetchone()
        if updated_user:
            return updated_user[0]
