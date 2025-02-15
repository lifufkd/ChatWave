import secrets
from pydantic import computed_field, Field
from pydantic_settings import BaseSettings
from pathlib import Path


class DBSettings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str = "postgres"
    DB_HOST: str = "postgres"
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
    REDIS_HOST: str = "redis"
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
    JWT_SECRET_KEY: str = Field(default_factory=lambda: JWTSettings.generate_and_store_secret())
    JWT_ACCESS_TOKEN_EXPIRES: int = 1209600

    @staticmethod
    def generate_and_store_secret() -> str:
        env_path = Path(".env")
        existing_env = {}
        if env_path.exists():
            with env_path.open("r", encoding="utf-8") as f:
                for line in f:
                    if "=" not in line:
                        continue

                    key, value = line.strip().split("=", 1)
                    existing_env[key] = value

        if "JWT_SECRET_KEY" in existing_env:
            return existing_env["JWT_SECRET_KEY"]
        new_secret = secrets.token_hex(32)
        with env_path.open("a", encoding="utf-8") as f:
            f.write(f"\nJWT_SECRET_KEY={new_secret}\n")

        return new_secret

    class Config:
        env_file = ".env"
        extra = "allow"


class GenericSettings(BaseSettings):
    MEDIA_FOLDER: Path
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
