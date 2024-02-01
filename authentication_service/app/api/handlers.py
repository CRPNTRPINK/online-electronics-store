from typing import Optional, Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Row, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import create_access_token
from app.db.dals import UserDAL
from app.db.models import User
from app.db.session import get_db
from app.dependecies import get_current_user
from app.schemas import DeleteUserResponse
from app.schemas import ShowUser
from app.schemas import Token, TokenData
from app.schemas import UpdateUserRequest
from app.schemas import UserCreate

user_router = APIRouter(prefix="/user", tags=["user"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def _create_new_user(body: UserCreate, db: AsyncSession) -> User:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user_exists = await user_dal.get_user_by_email(email=body.email)
            if user_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Пользователь с email: {body.email} уже существует"
                )
            hashed_password = get_password_hash(body.password)
            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
                hashed_password=hashed_password
            )

            return user


async def _delete_user(user_id: UUID, db: AsyncSession) -> Optional[UUID]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user_id = await user_dal.delete_user(user_id=user_id)

            return user_id


async def _get_user_by_id(user_id: UUID, db: AsyncSession) -> Optional[User]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.get_user_by_id(user_id=user_id)
            return user


async def _get_users(db: AsyncSession) -> Optional[Sequence[Row[tuple[User]]]]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            users = await user_dal.get_users()
            return users


async def _authenticate_user(email: str, db: AsyncSession) -> Optional[User]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.get_user_by_email(email=email)
            return user


async def _update_user(
        user_id: UUID, body: UpdateUserRequest, db: AsyncSession
) -> Optional[User]:
    body = body.model_dump(exclude_none=True)
    if not body:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one parameter for user update info should be provided",
        )
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            body = body
            user = await user_dal.update_user(user_id=user_id, **body)

            return user


def get_password_hash(password):
    return pwd_context.hash(password)


def get_current_active_user(current_user: Annotated[ShowUser, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate,
                      db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        user = await _create_new_user(body, db)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.args[0])
    except AttributeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.args[0])

    return ShowUser.model_validate(user, strict=True)


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(
        user_id: UUID, db: AsyncSession = Depends(get_db)
) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id, db)

    if not deleted_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id: {user_id} not found.",
        )

    return DeleteUserResponse(user_id=deleted_user_id)


@user_router.get("/get-user-by-id", response_model=ShowUser)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await _get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id: {user} not found.",
        )

    return ShowUser.model_validate(user)


@user_router.get('/', response_model=List[ShowUser])
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await _get_users(db)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователи не найдены",
        )
    return [ShowUser.model_validate(user[0]) for user in users]


@user_router.put("/", response_model=ShowUser)
async def update_user(
        user_id: UUID,
        body: UpdateUserRequest,
        db: AsyncSession = Depends(get_db)
) -> ShowUser:
    try:
        user = await _update_user(user_id, body, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user with id: {user} not found.",
            )
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.args[0])

    return ShowUser.model_validate(user)


@user_router.post("/token")
async def login_for_access_token(form_data=Depends(OAuth2PasswordRequestForm),
                                 db: AsyncSession = Depends(get_db)):
    user = await _authenticate_user(form_data.username, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"user with username: {form_data.username} not found.",
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"wrong password",
        )

    role = 1  # TODO добавить роли
    access_token = create_access_token(data={"sub": str(user.user_id), "role": role})
    response = JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"message": "Operation completed successfully"})
    response.set_cookie(key="token", value=f"Bearer {access_token}")
    return response


@user_router.get("/token_verify", response_model=TokenData)
def verify_token(user: Annotated[ShowUser, Depends(get_current_active_user)]):
    return user
