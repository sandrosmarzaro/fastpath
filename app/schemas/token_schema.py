from pydantic import BaseModel

from app.core.settings import settings


class TokenBase(BaseModel):
    pass


class TokenResponse(TokenBase):
    access_token: str
    token_type: str | None = settings.TOKEN_TYPE
