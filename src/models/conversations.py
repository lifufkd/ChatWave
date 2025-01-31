from sqlalchemy import ForeignKey, text, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import OrmBase
from storage import FileManager
from utilities import (
    text_not_required_type,
    datetime_auto_set,
    ConversationTypes,
    primary_key_type,
    datetime_auto_update, MediaPatches
)


class Conversations(OrmBase):
    __tablename__ = 'conversations'
    id: Mapped[primary_key_type]
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    type: Mapped[ConversationTypes] = mapped_column()
    name: Mapped[str] = mapped_column(String(64), nullable=True)
    description: Mapped[text_not_required_type]
    avatar_name: Mapped[text_not_required_type]
    avatar_type: Mapped[text_not_required_type]
    created_at: Mapped[datetime_auto_set]
    updated_at: Mapped[datetime_auto_update]

    creator: Mapped["Users"] = relationship(
        back_populates="owned_conversations"
    )
    members: Mapped[list["Users"]] = relationship(
        back_populates="conversations",
        secondary=f"{OrmBase.metadata.schema}.conversations_members"
    )
    messages: Mapped[list["Messages"]] = relationship(
        back_populates="conversation"
    )
    calls: Mapped[list["Calls"]] = relationship(
        back_populates="conversation"
    )
    unread_messages: Mapped[list["UnreadMessages"]] = relationship()


# async def delete_media_file(mapper, connection, target):
#     if target.avatar_name:
#         file_path = MediaPatches.GROUPS_AVATARS_FOLDER.value / target.avatar_name
#         await FileManager().delete_file(file_path=file_path)
#
#
# event.listen(Conversations, "after_delete", delete_media_file)


