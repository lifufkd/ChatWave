import sys
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from utilities import db_settings, AppModes, generic_settings


if generic_settings.MODE == AppModes.PRODUCTION.value or generic_settings.MODE == AppModes.DEVELOPMENT.value:
    engine = create_async_engine(db_settings.sqlalchemy_postgresql_url)
elif generic_settings.MODE == AppModes.TESTING.value:
    engine = create_async_engine(db_settings.test_sqlalchemy_postgresql_url)
else:
    sys.exit("Invalid launch mode specified! Only production, development and testing are supported!")

session = async_sessionmaker(bind=engine)


class OrmBase(DeclarativeBase):
    metadata = MetaData(schema=db_settings.DB_SCHEMA)
