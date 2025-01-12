from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from utilities.config import db_settings


engine = create_async_engine(db_settings.postgresql_url)
session = async_sessionmaker(bind=engine)


class OrmBase(DeclarativeBase):
    metadata = MetaData(schema=db_settings.DB_SCHEMA)

