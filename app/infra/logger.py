import logging

import click
import structlog
from rich.traceback import install
from structlog.processors import CallsiteParameter, CallsiteParameterAdder
from structlog.stdlib import BoundLogger
from structlog.typing import Processor

from app.infra.environment_variables import environment_variables


def configure_logger() -> None:
    log_level = logging.INFO
    if environment_variables.DEPLOY_MODE == "DEVELOPMENT":
        log_level = logging.DEBUG
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[logging.StreamHandler()],
    )
    processors: list[Processor] = [
        structlog.stdlib.add_log_level,
        structlog.dev.set_exc_info,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso", utc=False),
        CallsiteParameterAdder(
            [
                CallsiteParameter.FILENAME,
                CallsiteParameter.LINENO,
                CallsiteParameter.FUNC_NAME,
            ]
        ),
    ]
    if environment_variables.DEPLOY_MODE == "DEVELOPMENT":
        _ = install(show_locals=True, suppress=[click], max_frames=3)
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


configure_logger()
logger: BoundLogger = structlog.get_logger()
