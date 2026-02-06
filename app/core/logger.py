import logging.config
from abc import abstractmethod
from functools import lru_cache

import structlog
from uuid6 import uuid7

from app.core.settings import settings


def _drop_color_message(
    _logger: object, _method: str, event_dict: dict
) -> dict:
    event_dict.pop('color_message', None)
    return event_dict


class Logger[RendererType]:
    def __init__(self) -> None:
        self.level = settings.LOG_LEVEL
        self._configure_log()

    @classmethod
    @abstractmethod
    def get_renderer(cls) -> RendererType: ...

    @classmethod
    def _get_processors(cls) -> list:
        return [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.UnicodeDecoder(),
            structlog.processors.StackInfoRenderer(),
        ]

    def _configure_log(self) -> None:
        logging.config.dictConfig(
            {
                'version': 1,
                'disable_existing_loggers': True,
                'formatters': {
                    'main_fmt': {
                        '()': structlog.stdlib.ProcessorFormatter,
                        'processors': [
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            self.get_renderer(),
                        ],
                        'foreign_pre_chain': [
                            *self._get_processors(),
                            structlog.stdlib.ExtraAdder(),
                            _drop_color_message,
                        ],
                    },
                },
                'handlers': {
                    'main_handler': {
                        'level': self.level,
                        'class': 'logging.StreamHandler',
                        'formatter': 'main_fmt',
                    },
                },
                'root': {
                    'handlers': ['main_handler'],
                    'level': self.level,
                },
                'loggers': {
                    'main_log': {
                        'handlers': ['main_handler'],
                        'level': self.level,
                        'propagate': False,
                    },
                    **{
                        logger: {
                            'handlers': [],
                            'propagate': True,
                        }
                        for logger in [
                            'uvicorn',
                            'sqlalchemy',
                        ]
                    },
                },
            }
        )

        structlog.configure_once(
            processors=[
                *self._get_processors(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    def get_logger(self, name: str = 'root') -> structlog.stdlib.BoundLogger:
        return structlog.getLogger(name)


class Development(Logger[structlog.dev.ConsoleRenderer]):
    @classmethod
    def get_renderer(cls) -> structlog.dev.ConsoleRenderer:
        return structlog.dev.ConsoleRenderer(colors=True)


class Production(Logger[structlog.processors.JSONRenderer]):
    @classmethod
    def get_renderer(cls) -> structlog.processors.JSONRenderer:
        return structlog.processors.JSONRenderer()


@lru_cache
def create_logger_instance() -> 'Logger':
    if settings.DEBUG:
        return Development()
    return Production()


def get_logger(name: str = 'root') -> structlog.stdlib.BoundLogger:
    return create_logger_instance().get_logger(name)


def generate_correlation_id() -> str:
    return str(uuid7())
