from pathlib import Path
from pydantic_settings import BaseSettings

# Get the directory where this config file is located
BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: str = "3306"
    MYSQL_DB: str = "placement_portal"
    SECRET_KEY: str = "supersecretkey"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24

    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else ".env"
        env_file_encoding = "utf-8"

settings = Settings()
