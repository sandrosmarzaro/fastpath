from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import health_check_router, path_router

app = FastAPI(
    title='Fast Path',
    version='0.1.0',
    summary='',
    description='',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health_check_router.router)
app.include_router(path_router.router)
