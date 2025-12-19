from http import HTTPStatus

from fastapi import APIRouter, Depends

from app.exceptions.erros import UnauthorizedError
from app.schemas.health_check_schema import HealthCheckResponse
from app.services.user_service import get_current_user

router = APIRouter(
    prefix='/api/v1',
    tags=['health_check'],
    dependencies=[Depends(get_current_user)],
    responses={
        HTTPStatus.UNAUTHORIZED: {
            'description': HTTPStatus.UNAUTHORIZED.description,
            'model': UnauthorizedError.schema(),
        },
    },
)


@router.get('/')
async def get_health_check() -> HealthCheckResponse:
    return HealthCheckResponse()
