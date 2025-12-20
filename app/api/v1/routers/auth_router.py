from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.exceptions.erros import ContentError, UnauthorizedError
from app.models.user_model import UserModel
from app.schemas.token_schema import TokenResponse
from app.services.auth_service import AuthService
from app.services.user_service import get_current_user

InjectService = Annotated[AuthService, Depends()]
OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]

router = APIRouter(
    prefix='/api/v1/auth',
    tags=['auth'],
    responses={
        HTTPStatus.UNPROCESSABLE_CONTENT: {
            'description': HTTPStatus.UNPROCESSABLE_CONTENT.description,
            'model': ContentError.schema(),
        },
        HTTPStatus.UNAUTHORIZED: {
            'description': HTTPStatus.UNAUTHORIZED.description,
            'model': UnauthorizedError.schema(),
        },
    },
)


@router.post('/token', status_code=HTTPStatus.OK)
async def create_access_token(
    service: InjectService, form: OAuthForm
) -> TokenResponse:
    return await service.create_token_by_form(form)


@router.post('/refresh_token', status_code=HTTPStatus.OK)
async def refresh_access_token(
    service: InjectService, user: CurrentUser
) -> TokenResponse:
    return service.create_token_by_sub(user.username)
