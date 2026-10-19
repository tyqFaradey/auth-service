import logging
import sys


def setup_logging(
    level: int | str = logging.INFO,
) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/file.log", encoding="utf-8"),
        ],
    )


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name)
