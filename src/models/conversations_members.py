from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from database import OrmBase
from utilities import ConversationMemberRoles


class ConversationMembers(OrmBase):
    __tablename__ = 'conversations_members'
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        primary_key=True
    )

    role: Mapped[ConversationMemberRoles] = mapped_column(nullable=False, index=True)
    joined_at: Mapped[datetime] = mapped_column(
        nullable=False,
        index=True,
        server_default=text("TIMEZONE('utc', now())")
    )
