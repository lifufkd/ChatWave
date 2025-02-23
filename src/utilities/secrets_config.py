from pydantic_settings import BaseSettings
from pathlib import Path

from .random_generators import generate_jwt_token


class DBSettings(BaseSettings):
    DB_USER: str = "admin"
    DB_PASSWORD: str = "admin"
    DB_DATABASE: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_SCHEMA: str = "chatwave"

    @property
    def sqlalchemy_postgresql_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    @property
    def asyncpg_postgresql_url(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    class Config:
        env_file = ".env"
        extra = "allow"


class RedisSettings(BaseSettings):
    REDIS_USER: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_DATABASE: int = 0
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @property
    def redis_url(self):
        if self.REDIS_USER:
            redis_user = self.REDIS_USER
        else:
            redis_user = ""
        if self.REDIS_PASSWORD:
            redis_password = self.REDIS_PASSWORD
        else:
            redis_password = ""
        return f"redis://{redis_user}:{redis_password}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DATABASE}"

    class Config:
        env_file = ".env"
        extra = "allow"


class JWTSettings(BaseSettings):
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = generate_jwt_token()
    JWT_ACCESS_TOKEN_EXPIRES: int = 1209600

    class Config:
        env_file = ".env"
        extra = "allow"


class GenericSettings(BaseSettings):
    MEDIA_FOLDER: Path = Path("/app/data")
    ALLOWED_IMAGE_TYPES: list[str] = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
        "image/bmp",
        "image/tiff",
        "image/x-icon"
    ]

    ALLOWED_VIDEO_TYPES: list[str] = [
        "video/mp4",
        "video/webm",
        "video/ogg",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-flv",
        "video/x-matroska",
        "video/mpeg",
        "video/3gpp",
        "video/3gpp2"
    ]

    ALLOWED_AUDIO_TYPES: list[str] = [
        "audio/mpeg",
        "audio/wav",
        "audio/ogg",
        "audio/webm",
        "audio/aac",
        "audio/flac",
        "audio/x-wav",
        "audio/x-m4a",
        "audio/x-flac",
        "audio/mp4",
        "audio/midi",
        "audio/x-midi"
    ]
    MAX_UPLOAD_IMAGE_SIZE: int = 30
    MAX_UPLOAD_VIDEO_SIZE: int = 8192
    MAX_UPLOAD_AUDIO_SIZE: int = 512
    MAX_UPLOAD_FILE_SIZE: int = 16384
    CHUNK_SIZE: int = 16
    MAX_ITEMS_PER_REQUEST: int = 100

    class Config:
        env_file = ".env"
        extra = "allow"


redis_settings = RedisSettings()
db_settings = DBSettings()
jwt_settings = JWTSettings()
generic_settings = GenericSettings()
