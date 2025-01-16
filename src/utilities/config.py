from pydantic_settings import BaseSettings
from pathlib import Path


class DBSettings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_HOST: str
    DB_PORT: str
    DB_SCHEMA: str

    @property
    def postgresql_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    class Config:
        env_file = ".env"
        extra = "allow"


class RedisSettings(BaseSettings):
    REDIS_USER: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_DATABASE: int
    REDIS_HOST: str
    REDIS_PORT: str

    class Config:
        env_file = ".env"
        extra = "allow"


class JWTSettings(BaseSettings):
    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRES: int = 1209600

    class Config:
        env_file = ".env"
        extra = "allow"


class GenericSettings(BaseSettings):
    MEDIA_FOLDER: Path
    ALLOWED_MEDIA_TYPES: list[str] = ["image/jpeg", "image/png"]
    MAX_UPLOAD_SIZE: int = 30
    MAX_ITEMS_PER_REQUEST: int = 100

    class Config:
        env_file = ".env"
        extra = "allow"


redis_settings = RedisSettings()
db_settings = DBSettings()
jwt_settings = JWTSettings()
generic_settings = GenericSettings()
