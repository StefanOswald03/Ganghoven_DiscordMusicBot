import pathlib

from dotenv import load_dotenv
import os

dotenv_path = os.getenv("DOTENV_PATH", ".env")
load_dotenv(dotenv_path)

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
LAVALINK_URL = os.getenv("LAVALINK_URL")

BASE_DIR = pathlib.Path(__file__).parent
COGS_DIR = BASE_DIR / "cogs"
