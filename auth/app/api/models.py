import re
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import field_validator, model_validator

LATTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        from_attributes = True


class ShowUser(TunedModel):
    user_id: UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    name: str
    surname: str
    email: Optional[EmailStr]
    password: str
    password_confirm: str

    @field_validator("name")
    def validate_name(cls, value):
        if not LATTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Name should contains only letters",
            )
        return value

    @field_validator("surname")
    def validate_surname(cls, value):
        if not LATTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Surname should contains only letters",
            )
        return value

    @field_validator("password")
    def password_complexity(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        if not re.search("[a-z]", v):
            raise ValueError('Пароль должен содержать буквы нижнего регистра')
        if not re.search("[A-Z]", v):
            raise ValueError('Пароль должен содержать буквы верхнего регистра')
        if not re.search("[0-9]", v):
            raise ValueError('Пароль должен содержать цифры')
        return v

    @model_validator(mode='after')
    def passwords_match(self):
        pwd1 = self.password
        pwd2 = self.password_confirm
        if pwd1 != pwd2:
            raise ValueError('Пароли не совпадают')
        return self


class DeleteUserResponse(BaseModel):
    user_id: UUID


class UpdateUserRequest(UserCreate):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    password_confirm: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: UUID
