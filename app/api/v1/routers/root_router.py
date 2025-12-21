from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from app.core.settings import settings
from app.exceptions.erros import UnauthorizedError
from app.services.user_service import get_current_user

router = APIRouter(
    tags=['root'],
    dependencies=[Depends(get_current_user)],
    responses={
        HTTPStatus.UNAUTHORIZED: {
            'description': HTTPStatus.UNAUTHORIZED.description,
            'model': UnauthorizedError.schema(),
        },
    },
)


@router.get('/')
def redirect_root_to_swagger_or_health_check() -> RedirectResponse:
    if settings.DEBUG:
        return RedirectResponse(
            url='/api/v1/docs',
            status_code=HTTPStatus.TEMPORARY_REDIRECT,
        )
    return RedirectResponse(
        url='/api/v1/',
        status_code=HTTPStatus.TEMPORARY_REDIRECT,
    )
