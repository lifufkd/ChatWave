from sqlalchemy import String, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import date

from database import OrmBase
from utilities import datetime_type, text_type


class Users(OrmBase):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    nickname: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    birthday: Mapped[date] = mapped_column(nullable=True)
    bio: Mapped[text_type]
    avatar_url: Mapped[text_type]
    last_online: Mapped[datetime_type]
    created_at: Mapped[datetime_type]
    updated_at: Mapped[datetime_type]

    __table_args__ = (
        Index('ix_users_username_passwordhash', 'username', 'password_hash'),
    )

