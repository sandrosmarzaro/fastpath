from functools import lru_cache
from logging import Logger as Logging
from logging import config, getLogger


class Logger:
    def __init__(self, config_file: str = 'logging.ini') -> None:
        self._config_file = config_file
        self._configure_log()
        self._logger = getLogger('root')

    def _configure_log(self) -> None:
        config.fileConfig(self._config_file, disable_existing_loggers=False)

    def get_logger(self) -> Logging:
        return self._logger


@lru_cache
def create_logger_instance() -> Logger:
    return Logger()


def get_logger() -> Logging:
    return create_logger_instance().get_logger()
