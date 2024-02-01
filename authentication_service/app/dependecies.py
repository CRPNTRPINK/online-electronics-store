from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import ShowUser
from app.auth import verify_token
from app.db.dals import UserDAL
from app.db.session import get_db


class OAuth2PasswordBearerWithCookie(OAuth2):
    __hash__ = lambda obj: id(obj)

    def __init__(
            self,
            tokenUrl: str,
            scheme_name: str = None,
            scopes: dict = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlows(
            password={"tokenUrl": tokenUrl, "scopes": scopes}
        )
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        token = request.cookies.get("token")
        split_token = token.split()
        if not token or len(split_token) != 2:
            if self.auto_error:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        return split_token[1]


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="auth/user/token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> ShowUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.get_user_by_id(user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return ShowUser.model_validate(user)
