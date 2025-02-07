from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from utilities import db_settings


engine = create_async_engine(db_settings.sqlalchemy_postgresql_url, echo=True)
session = async_sessionmaker(bind=engine)


class OrmBase(DeclarativeBase):
    metadata = MetaData(schema=db_settings.DB_SCHEMA)
