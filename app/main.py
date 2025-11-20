from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import health_check_router, path_router
from app.core.settings import Settings
from app.exceptions.exception_handler import add_exceptions_handler

tags_metadata = [
    {
        'name': 'paths',
        'description': 'calculated the fast path',
    },
]

app = FastAPI(
    title='Fast Path',
    version='0.1.0',
    summary='API to calculate the fast delivery path.',
    description='',
    contact={
        'name': 'Sandro Smarzaro',
        'email': 'sansmarzaro@gmail.com',
        'url': 'https://www.linkedin.com/in/sandrosmarzaro/',
    },
    license_info={
        'name': 'The MIT License',
        'identifier': 'MIT',
        'url': 'https://opensource.org/license/mit',
    },
    docs_url=None if Settings().DEBUG is None else '/api/v1/docs',
    redoc_url=None if Settings().DEBUG is None else '/api/v1/redoc',
    openapi_url=None if Settings().DEBUG is None else '/api/v1/openapi.json',
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

add_exceptions_handler(app)

app.include_router(health_check_router.router)
app.include_router(path_router.router)
