from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database import OrmBase
from utilities import primary_key_type


class UnreadMessages(OrmBase):
    __tablename__ = 'unread_messages'
    id: Mapped[primary_key_type]
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey('conversations.id', ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete="CASCADE")
    )
    message_id: Mapped[int] = mapped_column(
        ForeignKey('messages.id', ondelete="CASCADE"),
        nullable=True
    )
    call_id: Mapped[int] = mapped_column(
        ForeignKey('calls.id', ondelete="CASCADE"),
        nullable=True
    )

    __table_args = (
        UniqueConstraint(
            "conversation_id",
            "user_id",
            "message_id",
            "call_id",
            name="unread_messages_conversation_id_user_id_message_id_call_id"),
    )
