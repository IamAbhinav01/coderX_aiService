import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Return a named, stdout-streaming logger.

    All loggers produced by this factory share the same format:
        2026-04-09 17:00:00 | INFO | app.services.question_generator | message

    The handler is only attached once (idempotent) so calling get_logger()
    multiple times for the same module name is safe.

    Args:
        name: typically __name__ from the calling module.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False  # prevent duplicate log lines from the root logger

    return logger
