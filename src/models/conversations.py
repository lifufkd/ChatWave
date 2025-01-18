from sqlalchemy import ForeignKey, text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from database import OrmBase
from utilities import text_not_required_type, datetime_auto_set, ConversationTypes, primary_key_type


class Conversations(OrmBase):
    __tablename__ = 'conversations'
    id: Mapped[primary_key_type]
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )
    type: Mapped[ConversationTypes] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=True)
    description: Mapped[text_not_required_type]
    avatar_name: Mapped[text_not_required_type]
    avatar_type: Mapped[text_not_required_type]
    created_at: Mapped[datetime_auto_set]
    updated_at: Mapped[datetime] = mapped_column(
        onupdate=text("TIMEZONE('utc', now())"),
        index=True,
        nullable=True
    )

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


