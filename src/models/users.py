from sqlalchemy import String, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import date

from database import OrmBase
from utilities import (
    datetime_auto_set,
    datetime_not_required_type,
    text_not_required_type,
    primary_key_type,
    datetime_auto_update
)


class Users(OrmBase):
    __tablename__ = "users"
    id: Mapped[primary_key_type]
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    nickname: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    birthday: Mapped[date] = mapped_column(nullable=True)
    bio: Mapped[text_not_required_type]
    last_online: Mapped[datetime_not_required_type]
    created_at: Mapped[datetime_auto_set]
    updated_at: Mapped[datetime_auto_update]

    blocked_user: Mapped[list["BlockedUsers"]] = relationship(foreign_keys="BlockedUsers.blocker_id")
    blocker_user: Mapped[list["BlockedUsers"]] = relationship(foreign_keys="BlockedUsers.blocker_id")
    owned_conversations: Mapped[list["Conversations"]] = relationship(
        back_populates="creator"
    )
    conversations: Mapped[list["Conversations"]] = relationship(
        back_populates="members",
        secondary=f"{OrmBase.metadata.schema}.conversations_members"
    )
    messages: Mapped[list["Messages"]] = relationship(
        back_populates="sender"
    )
    calls: Mapped[list["Calls"]] = relationship(
        back_populates="caller"
    )
    unread_messages: Mapped[list["UnreadMessages"]] = relationship()

    __table_args__ = (
        Index('ix_users_username_passwordhash', 'username', 'password_hash'),
    )

