from pydantic_settings import BaseSettings


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


redis_settings = RedisSettings()
db_settings = DBSettings()
