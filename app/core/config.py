from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "SMARTFS"
    APP_ENV: str = "dev"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    DATABASE_URL: str = Field(default="postgresql+psycopg://smartfs:smartfsstrongpass@db:5432/smartfs")

    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields in .env without error

settings = Settings()