from sqlalchemy import text, Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from database import OrmBase
from utilities import datetime_not_required_type, primary_key_type, CallsStatus


class Calls(OrmBase):
    __tablename__ = 'calls'
    id: Mapped[primary_key_type]
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey('conversations.id'),
        index=True
    )
    caller_id: Mapped[int] = mapped_column(
        ForeignKey('users.id')
    )
    status: Mapped[CallsStatus] = mapped_column(nullable=False)
    duration: Mapped[int] = mapped_column(nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        index=True,
        nullable=False
    )
    finished_at: Mapped[datetime_not_required_type]

    conversation: Mapped["Conversations"] = relationship(
        back_populates="calls"
    )
    caller: Mapped["Users"] = relationship(
        back_populates="calls",
    )
    unread_messages: Mapped[list["UnreadMessages"]] = relationship()
