from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import date

from database import OrmBase
from utilities import (
    datetime_auto_set,
    datetime_not_required_type,
    text_not_required_type,
    primary_key_type,
    datetime_auto_update,
    text_required_type
)


class Users(OrmBase):
    __tablename__ = "users"
    id: Mapped[primary_key_type]
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True, nullable=False)
    password_hash: Mapped[text_required_type]
    nickname: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    birthday: Mapped[date] = mapped_column(nullable=True)
    bio: Mapped[text_not_required_type]
    avatar_name: Mapped[text_not_required_type]
    avatar_type: Mapped[text_not_required_type]
    last_online: Mapped[datetime_not_required_type]
    created_at: Mapped[datetime_auto_set]
    updated_at: Mapped[datetime_auto_update]

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


# async def delete_media_file(mapper, connection, target):
#     if target.avatar_name:
#         file_path = MediaPatches.USERS_AVATARS_FOLDER.value / target.avatar_name
#         await FileManager().delete_file(file_path=file_path)
#
#
# event.listen(Users, "after_delete", delete_media_file)
