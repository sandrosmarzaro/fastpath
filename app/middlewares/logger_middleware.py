import structlog
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.logger import generate_correlation_id


class LoggerMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)

        structlog.contextvars.bind_contextvars(
            correlation_id=generate_correlation_id(),
            method=scope['method'],
            path=scope['path'],
        )

        try:
            await self.app(scope, receive, send)
        finally:
            structlog.contextvars.unbind_contextvars(
                'correlation_id', 'method', 'path'
            )
