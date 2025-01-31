from sqlalchemy import text, Index, event, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import OrmBase
from storage import FileManager
from utilities import (
    primary_key_type,
    MessagesStatus,
    text_not_required_type,
    MessagesTypes,
    datetime_auto_set,
    datetime_auto_update,
    MediaPatches
)


class Messages(OrmBase):
    __tablename__ = 'messages'
    id: Mapped[primary_key_type]
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey('conversations.id', ondelete="CASCADE"),
        index=True
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete="CASCADE"),
        index=True
    )
    status: Mapped[MessagesStatus] = mapped_column(nullable=False, index=True)
    type: Mapped[MessagesTypes] = mapped_column(nullable=True)
    content: Mapped[text_not_required_type]
    file_content_name: Mapped[text_not_required_type]
    file_content_type: Mapped[text_not_required_type]
    created_at: Mapped[datetime_auto_set]
    updated_at: Mapped[datetime_auto_update]

    conversation: Mapped["Conversations"] = relationship(
        back_populates="messages"
    )
    sender: Mapped["Users"] = relationship(
        back_populates="messages",
    )
    unread_messages: Mapped[list["UnreadMessages"]] = relationship()

    __table_args = (
        Index("ix_messages_created_at_content", "created_at", "content"),
    )


# async def delete_media_file(mapper, connection, target):
#     if target.file_content_name:
#         file_path = MediaPatches.MEDIA_MESSAGES_FOLDER.value / target.file_content_name
#         await FileManager().delete_file(file_path=file_path)
#
#
# event.listen(Messages, "before_delete", delete_media_file)



