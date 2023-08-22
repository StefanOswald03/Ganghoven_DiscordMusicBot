import pathlib

from dotenv import load_dotenv
import os

dotenv_path = os.getenv("DOTENV_PATH", ".env")
load_dotenv(dotenv_path)

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
LAVALINK_URL = os.getenv("LAVALINK_URL")

BASE_DIR = pathlib.Path(__file__).parent
COGS_DIR = BASE_DIR / "cogs"

SPOTIFY_CLIENT = os.getenv("SPOTIFY_CLIENT")
SPOTIFY_PASSWORD = os.getenv("SPOTIFY_PASSWORD")

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_Loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {
            "format": "%(levelname)-105 - %(name)-15s : %(message)s"
        }
    },
    "handlers": {
        "console": {
            'Level': 'DEBUG',
            'class': "logging. StreamHandler",
            "formatter": "simple"
        },
        'console2': {
            'Level': "WARNING",
            'class': "Logging.StreamHandler",
            'formatter': "simple"
        },
        "file": {
            'Level': "INFO",
            'class': "logging.FileHandler",
            "filename": "Logs/infos. Log",
            'mode': "w"
        }
    },
    "Loggers": {
        "bot": {
            'handlers': ['console'],
            "Level": "INFO",
            "propagate": False
        },
        "discord": {
            "handlers": ["console2", "file"],
            "Level": "INFO",
            "propagate": False
        }
    }
}
