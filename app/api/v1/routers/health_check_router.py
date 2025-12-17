from fastapi import APIRouter, Depends

from app.schemas.health_check_schema import HealthCheckResponse
from app.services.user_service import get_current_user

router = APIRouter(
    prefix='/api/v1',
    tags=['health_check'],
    dependencies=[Depends(get_current_user)],
)


@router.get('/')
async def get_health_check() -> HealthCheckResponse:
    return HealthCheckResponse()
