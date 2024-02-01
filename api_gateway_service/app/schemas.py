from pydantic import BaseModel
from uuid import UUID


class ShowUser(BaseModel):
    user_id: UUID
