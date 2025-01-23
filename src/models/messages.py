from sqlalchemy import text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from database import OrmBase
from utilities import (
    primary_key_type,
    MessagesStatus,
    text_not_required_type,
    MessagesTypes)


class Messages(OrmBase):
    __tablename__ = 'messages'
    id: Mapped[primary_key_type]
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey('conversations.id', ondelete="CASCADE"),
        index=True
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete="CASCADE"),
    )
    status: Mapped[MessagesStatus] = mapped_column()
    type: Mapped[MessagesTypes] = mapped_column(nullable=True)
    content: Mapped[text_not_required_type]
    file_content_name: Mapped[text_not_required_type]
    file_content_type: Mapped[text_not_required_type]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        index=True,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        onupdate=text("TIMEZONE('utc', now())"),
        index=True,
        nullable=True
    )

    conversation: Mapped["Conversations"] = relationship(
        back_populates="messages"
    )
    sender: Mapped["Users"] = relationship(
        back_populates="messages",
    )
    unread_messages: Mapped[list["UnreadMessages"]] = relationship()



