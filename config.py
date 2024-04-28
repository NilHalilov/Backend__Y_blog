import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings

if not find_dotenv():
    exit("File '.env' does not exist.")
else:
    load_dotenv()


class SettingsDB(BaseSettings):
    db_url: str
    db_echo: bool = False
    # db_echo: bool = True


BASE_PATH = Path(__file__).parent
MEDIA_PATH = f"{BASE_PATH}/media/"
AllOWED_IMG_EXTENSIONS = ("png", "jpg", "jpeg", "gif")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

DB_USER_TEST = os.getenv("DB_USER_TEST")
DB_PASSWORD_TEST = os.getenv("DB_PASSWORD_TEST")
DB_NAME_TEST = os.getenv("DB_NAME_TEST")
DB_HOST_TEST = os.getenv("DB_HOST_TEST")
DB_PORT_TEST = os.getenv("DB_PORT_TEST")

DB_PATH = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
TEST_DB_PATH = f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASSWORD_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"

settings_db = SettingsDB(db_url=DB_PATH)
