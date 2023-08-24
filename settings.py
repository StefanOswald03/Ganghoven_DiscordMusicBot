import pathlib
import logging
from logging.config import dictConfig
from dotenv import load_dotenv
import os

dotenv_path = os.getenv("DOTENV_PATH", ".env")
load_dotenv(dotenv_path)

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
LAVALINK_URL = os.getenv("LAVALINK_URL")
MUSIXMATCH_API_KEY = os.getenv("MUSIXMATCH_API_KEY")


BASE_DIR = pathlib.Path(__file__).parent
COGS_DIR = BASE_DIR / "cogs"

SPOTIFY_CLIENT = os.getenv("SPOTIFY_CLIENT")
SPOTIFY_PASSWORD = os.getenv("SPOTIFY_PASSWORD")

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {"format": "%(levelname)-10s - %(name)-15s : %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/infos.log",
            "mode": "w",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)
